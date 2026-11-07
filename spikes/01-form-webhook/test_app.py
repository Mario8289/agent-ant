import xml.etree.ElementTree as ET

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

SYNTHETIC = {"CallSid": "CA00000000000000000000000000000000", "From": "+447000000000", "To": "+447000000001"}


def test_form_encoded_post_returns_twiml() -> None:
    response = client.post("/webhook/voice", data=SYNTHETIC)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    root = ET.fromstring(response.text)
    assert root.tag == "Response"
    assert root.find("Say") is not None


def test_missing_fields_are_rejected() -> None:
    response = client.post("/webhook/voice", data={"CallSid": "CA1"})
    assert response.status_code == 422
