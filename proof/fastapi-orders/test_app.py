from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_normalizes_and_serializes_order():
    response = client.post("/orders", json={"customer": " Ada ", "quantity": 2})
    assert response.status_code == 200
    assert response.json() == {"customer": "Ada", "quantity": 2}


def test_rejects_blank_customer():
    assert (
        client.post("/orders", json={"customer": " ", "quantity": 2}).status_code == 422
    )


def test_rejects_nonpositive_quantity():
    assert (
        client.post("/orders", json={"customer": "Ada", "quantity": 0}).status_code
        == 422
    )


def test_rejects_extra_fields():
    assert (
        client.post(
            "/orders", json={"customer": "Ada", "quantity": 2, "admin": True}
        ).status_code
        == 422
    )


def test_rejects_missing_quantity():
    assert client.post("/orders", json={"customer": "Ada"}).status_code == 422


def test_reads_settings(monkeypatch):
    monkeypatch.setenv("ZIPPER_PROOF_SERVICE_NAME", "Proof service")
    assert client.get("/health").json() == {"service": "Proof service"}
