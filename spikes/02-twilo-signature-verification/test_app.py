# =============================================================================
# Why the signature is base64, and why .encode()/.decode() show up everywhere
# -----------------------------------------------------------------------------
# HTTP headers can only carry ASCII text, never raw binary. A header value is a
# string of printable characters, so arbitrary bytes (like an HMAC digest)
# cannot go in a header as-is.
#
# An HMAC-SHA1 digest is 20 raw bytes that can contain any value 0-255,
# including non-printable / control characters, e.g.:
#
#     b'/\xf3\x87\xe5\x8c\xa5,>MD\xa2\xe5\xb5\xda\xb0J\xf4\xb4\x06u'
#
# To send that in a header, Twilio base64-encodes it into printable ASCII:
#
#     b'L/OH5YylLD5NRKLltdqwSvS0BnU='
#
# Two DIFFERENT "encodes" are in play and are easy to confuse:
#
#   1. Text encode/decode  (.encode() / .decode())  -- changes the TYPE
#      str <-> bytes. Crypto needs bytes, so the token and payload are
#      .encode()d (UTF-8) before hashing.
#
#   2. Base64 encode       (base64.b64encode)        -- changes the FORMAT
#      raw binary -> printable ASCII. Makes bytes header-safe. Output is still
#      bytes, so we .decode() it to a str for the header / compare_digest.
#
# Full pipeline (text -> bytes -> text):
#
#   token   (str)  --.encode()-->  bytes  --\
#                                             +--> hmac.new(...).digest() -> bytes (20 raw)
#   payload (str)  --.encode()-->  bytes  --/
#                                                --b64encode--> bytes (ASCII) --.decode()--> str
#
# The trailing .decode() does NOT undo the base64; it just converts the ASCII
# bytes into a str. (Undoing base64 would be base64.b64decode, a different call.)
# =============================================================================

import xml.etree.ElementTree as ET

from app import AUTH_TOKEN, app
from fastapi.testclient import TestClient
from signature import compute_signature

client = TestClient(app)

# The URL FastAPI sees when TestClient posts to this app. Twilio signs the URL
# exactly as the app reconstructs it, so the test must sign the same string.
WEBHOOK_URL = str(client.base_url).rstrip("/") + "/webhook/voice"

SYNTHETIC = {
    "CallSid": "CA00000000000000000000000000000000",
    "From": "+447000000000",
    "To": "+447000000001",
}


def test_compute_signature_matches_twilio_example() -> None:
    # Independent check against Twilio's published worked example, so the test
    # proves the algorithm matches Twilio rather than just agreeing with itself.
    url = "https://example.com/myapp.php?foo=1&bar=2"
    params = {
        "CallSid": "CA1234567890ABCDE",
        "Caller": "+14158675310",
        "Digits": "1234",
        "From": "+14158675310",
        "To": "+18005551212",
    }
    assert compute_signature(url, params, "12345") == "L/OH5YylLD5NRKLltdqwSvS0BnU="


def test_valid_signature_is_accepted() -> None:
    signature = compute_signature(WEBHOOK_URL, SYNTHETIC, AUTH_TOKEN)
    response = client.post(
        "/webhook/voice",
        data=SYNTHETIC,
        headers={"X-Twilio-Signature": signature},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    root = ET.fromstring(response.text)
    assert root.tag == "Response"


def test_tampered_body_is_rejected() -> None:
    # Attacker changes a field but keeps the original signature: must be 403.
    signature = compute_signature(WEBHOOK_URL, SYNTHETIC, AUTH_TOKEN)
    tampered = {**SYNTHETIC, "From": "+447999999999"}
    response = client.post(
        "/webhook/voice",
        data=tampered,
        headers={"X-Twilio-Signature": signature},
    )
    assert response.status_code == 403


def test_missing_signature_is_rejected() -> None:
    response = client.post("/webhook/voice", data=SYNTHETIC)
    assert response.status_code == 403
