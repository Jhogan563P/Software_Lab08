import pytest
from datetime import UTC, datetime

from app.services.dinner_service.application.use_cases import RegisterDinnerUseCase
from app.services.dinner_service.domain.entities import DinnerTransaction
from app.services.notifications_service.infrastructure.messaging.publisher import RabbitRewardProcessedPublisher
from app.services.rewards_service.application.use_cases import ProcessRewardUseCase
from app.services.rewards_service.infrastructure.messaging.consumer import RabbitRewardConsumer
from app.services.rewards_service.infrastructure.repository.in_memory import InMemoryRewardRepository

pytestmark = pytest.mark.e2e


class FakeDinnerPublisher:
    def __init__(self):
        self.messages = []

    def publish_dinner(self, dinner):
        self.messages.append(dinner)


class FakeRewardProcessedPublisher:
    def __init__(self):
        self.messages = []

    def publish(self, payload):
        self.messages.append(payload)


def test_end_to_end_reward_and_notification_flow():
    dinner_publisher = FakeDinnerPublisher()
    dinner_uc = RegisterDinnerUseCase(dinner_publisher)
    rewards_repo = InMemoryRewardRepository()
    rewards_uc = ProcessRewardUseCase(rewards_repo)
    reward_processed_publisher = FakeRewardProcessedPublisher()
    consumer = RabbitRewardConsumer(rewards_uc, reward_processed_publisher)

    dinner = DinnerTransaction(
        amount=100.0,
        card_number="4111111111111111",
        restaurant_id="R1",
        timestamp=datetime.now(UTC),
    )

    dinner_uc.execute(dinner)
    assert len(dinner_publisher.messages) == 1

    consumer._on_message(
        type("Channel", (), {"basic_ack": lambda self, delivery_tag: None})(),
        type("Method", (), {"delivery_tag": 1})(),
        None,
        b'{"amount":100.0,"card_number":"4111111111111111","restaurant_id":"R1","timestamp":"2026-05-30T00:00:00+00:00"}',
    )

    assert len(reward_processed_publisher.messages) == 1
    assert reward_processed_publisher.messages[0]["customer_id"] == "1111"
