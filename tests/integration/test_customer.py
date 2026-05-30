from fastapi.testclient import TestClient

from app.entrypoints.api.main import app, customer_repository


def test_register_customer_endpoint():
    client = TestClient(app)
    payload = {"customer_id": "C001", "name": "Jesus Perez", "email": "jesus@example.com"}

    response = client.post("/customers", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "created"
    stored = customer_repository.get("C001")
    assert stored is not None
    assert stored.name == "Jesus Perez"
