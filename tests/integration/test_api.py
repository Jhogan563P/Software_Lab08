from fastapi.testclient import TestClient
from app.entrypoints.api.main import app


def test_register_dinner_endpoint(monkeypatch):
    class FakePublisher:
        def publish_dinner(self, dinner):
            self.last = dinner

    fake = FakePublisher()

    def fake_create_publisher():
        return fake

    monkeypatch.setattr("app.entrypoints.api.main.create_publisher", fake_create_publisher)

    client = TestClient(app)
    payload = {"amount": 50.0, "card_number": "4111111111111111", "restaurant_id": "R1"}
    response = client.post("/dinner", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "published"
