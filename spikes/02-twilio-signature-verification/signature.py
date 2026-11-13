"""Spike 2: reproduce Twilio's X-Twilio-Signature algorithm.

Twilio signs every webhook with HMAC-SHA1 over the request URL plus the sorted
form parameters, keyed by the account AuthToken. The signature arrives in the
X-Twilio-Signature header.

This module holds the pure crypto so the web handler and the tests share it.
`compute_signature` is Twilio's side (used by tests to forge requests);
`validate_signature` is our side (used by the app to check requests).
"""

import base64
import hashlib
import hmac


def build_payload(url: str, params: dict[str, str]) -> str:
    """Concatenate the URL and the sorted parameter names/values.

    Twilio appends each parameter as ``namevalue`` with *no* delimiter, in
    case-sensitive alphabetical order by name, to the end of the URL string.
    """
    sorted_params = "".join(f"{name}{value}" for name, value in sorted(params.items()))
    return f"{url}{sorted_params}"


def compute_signature(url: str, params: dict[str, str], auth_token: str) -> str:
    """Replicate the signature Twilio attaches to a request (the signing side)."""
    payload = build_payload(url, params)
    digest = hmac.new(auth_token.encode(), payload.encode(), hashlib.sha1).digest()
    return base64.b64encode(digest).decode()


def validate_signature(url: str, params: dict[str, str], signature: str, auth_token: str) -> bool:
    """Return True when ``signature`` matches the recomputed value.

    Uses ``hmac.compare_digest`` so the comparison is constant-time and does not
    leak how many leading bytes matched (a timing attack).
    """
    expected = compute_signature(url, params, auth_token)
    return hmac.compare_digest(expected, signature)
