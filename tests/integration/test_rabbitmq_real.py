import os
import time
from datetime import UTC, datetime

import pytest

from app.services.dinner_service.domain.entities import DinnerTransaction
from app.services.dinner_service.infrastructure.messaging.rabbit_publisher import RabbitDinnerPublisher
from app.services.notifications_service.application.use_cases import NotifyRewardProcessedUseCase
from app.services.notifications_service.infrastructure.delivery.in_memory import InMemoryNotificationSender
from app.services.notifications_service.infrastructure.messaging.consumer import RabbitNotificationConsumer
from app.services.notifications_service.infrastructure.messaging.publisher import RabbitRewardProcessedPublisher
from app.services.rewards_service.application.use_cases import ProcessRewardUseCase
from app.services.rewards_service.infrastructure.messaging.consumer import RabbitRewardConsumer
from app.services.rewards_service.infrastructure.repository.in_memory import InMemoryRewardRepository
from app.shared.messaging.rabbitmq import RabbitConnectionFactory


pytestmark = [
    pytest.mark.real,
    pytest.mark.skipif(
        not os.getenv("RABBIT_HOST") or not os.getenv("RABBIT_USER") or not os.getenv("RABBIT_PASS"),
        reason="RabbitMQ environment variables are required for the real integration test.",
    )
]


def _drain_queue(queue_name: str) -> None:
    connection = RabbitConnectionFactory().create_connection()
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_purge(queue=queue_name)
    finally:
        connection.close()


def _wait_for_message(queue_name: str, attempts: int = 20, delay: float = 0.1):
    connection = RabbitConnectionFactory().create_connection()
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        for _ in range(attempts):
            method, properties, body = channel.basic_get(queue=queue_name, auto_ack=False)
            if method is not None:
                return connection, channel, method, properties, body
            time.sleep(delay)
        pytest.fail(f"No message received from queue {queue_name!r}.")
    except Exception:
        connection.close()
        raise


def test_real_rabbitmq_flow_round_trip():
    _drain_queue("laboratorio_1")
    _drain_queue("rewards_processed")

    dinner_publisher = RabbitDinnerPublisher()
    rewards_repo = InMemoryRewardRepository()
    rewards_uc = ProcessRewardUseCase(rewards_repo)
    reward_processed_publisher = RabbitRewardProcessedPublisher()
    reward_consumer = RabbitRewardConsumer(rewards_uc, reward_processed_publisher)

    sender = InMemoryNotificationSender()
    notification_uc = NotifyRewardProcessedUseCase(sender)
    notification_consumer = RabbitNotificationConsumer(notification_uc)

    dinner = DinnerTransaction(
        amount=100.0,
        card_number="4111111111111111",
        restaurant_id="R1",
        timestamp=datetime.now(UTC),
    )

    dinner_publisher.publish_dinner(dinner)

    dinner_connection, dinner_channel, dinner_method, dinner_properties, dinner_body = _wait_for_message("laboratorio_1")
    try:
        reward_consumer._on_message(dinner_channel, dinner_method, dinner_properties, dinner_body)
    finally:
        dinner_connection.close()

    reward_connection, reward_channel, reward_method, reward_properties, reward_body = _wait_for_message("rewards_processed")
    try:
        notification_consumer._on_message(reward_channel, reward_method, reward_properties, reward_body)
    finally:
        reward_connection.close()

    assert len(sender.sent) == 1
    assert sender.sent[0].customer_id == "1111"
    assert sender.sent[0].channel == "email"
