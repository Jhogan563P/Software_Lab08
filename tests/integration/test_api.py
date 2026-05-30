import pytest
from fastapi.testclient import TestClient
from app.services.dinner_service.main import app

pytestmark = pytest.mark.integration


def test_register_dinner_endpoint(monkeypatch):
    class FakePublisher:
        def publish_dinner(self, dinner):
            self.last = dinner

    fake = FakePublisher()

    def fake_create_publisher():
        return fake

    monkeypatch.setattr("app.services.dinner_service.main.create_publisher", fake_create_publisher)

    client = TestClient(app)
    payload = {"amount": 50.0, "card_number": "4111111111111111", "restaurant_id": "R1"}
    response = client.post("/dinner", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "published"
