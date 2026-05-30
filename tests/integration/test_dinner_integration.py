"""
Integration tests – DinnerService HTTP endpoint
Usa TestClient de FastAPI + monkeypatch para aislar el publisher de RabbitMQ.
Marker: integration
"""
import pytest
from fastapi.testclient import TestClient

from app.services.dinner_service.main import app
from app.services.dinner_service.domain.entities import DinnerTransaction

pytestmark = pytest.mark.integration


class FakeDinnerPublisher:
    def __init__(self):
        self.published: list[DinnerTransaction] = []

    def publish_dinner(self, dinner: DinnerTransaction) -> None:
        self.published.append(dinner)


@pytest.fixture()
def client_and_fake(monkeypatch):
    fake = FakeDinnerPublisher()
    monkeypatch.setattr(
        "app.services.dinner_service.main.create_publisher",
        lambda: fake,
    )
    return TestClient(app), fake


class TestDinnerEndpoint:
    def test_register_dinner_returns_200(self, client_and_fake):
        client, _ = client_and_fake
        response = client.post(
            "/dinner",
            json={"amount": 80.0, "card_number": "4111111111111111", "restaurant_id": "R5"},
        )
        assert response.status_code == 200

    def test_register_dinner_response_body(self, client_and_fake):
        client, _ = client_and_fake
        response = client.post(
            "/dinner",
            json={"amount": 80.0, "card_number": "4111111111111111", "restaurant_id": "R5"},
        )
        data = response.json()
        assert data["status"] == "published"
        assert data["queue"] == "laboratorio_1"

    def test_register_dinner_calls_publisher(self, client_and_fake):
        client, fake = client_and_fake
        client.post(
            "/dinner",
            json={"amount": 50.0, "card_number": "1234567890123456", "restaurant_id": "R2"},
        )
        assert len(fake.published) == 1
        assert fake.published[0].amount == 50.0

    def test_register_dinner_invalid_amount_rejected(self, client_and_fake):
        """amount debe ser > 0 (validado por pydantic Field gt=0)."""
        client, _ = client_and_fake
        response = client.post(
            "/dinner",
            json={"amount": 0.0, "card_number": "4111111111111111", "restaurant_id": "R1"},
        )
        assert response.status_code == 422

    def test_register_dinner_short_card_rejected(self, client_and_fake):
        """card_number debe tener al menos 12 caracteres."""
        client, _ = client_and_fake
        response = client.post(
            "/dinner",
            json={"amount": 50.0, "card_number": "12345", "restaurant_id": "R1"},
        )
        assert response.status_code == 422

    def test_register_dinner_sets_timestamp_when_omitted(self, client_and_fake):
        """Si no se envía timestamp, el endpoint lo genera."""
        client, fake = client_and_fake
        client.post(
            "/dinner",
            json={"amount": 75.0, "card_number": "4111111111111111", "restaurant_id": "R3"},
        )
        assert fake.published[0].timestamp is not None

    def test_register_multiple_dinners(self, client_and_fake):
        client, fake = client_and_fake
        for amount in [10.0, 20.0, 30.0]:
            client.post(
                "/dinner",
                json={"amount": amount, "card_number": "4111111111111111", "restaurant_id": "R1"},
            )
        assert len(fake.published) == 3
