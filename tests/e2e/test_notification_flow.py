import pytest
from app.services.notifications_service.application.use_cases import NotifyRewardProcessedUseCase
from app.services.notifications_service.infrastructure.delivery.in_memory import InMemoryNotificationSender
from app.services.notifications_service.infrastructure.messaging.consumer import RabbitNotificationConsumer

pytestmark = pytest.mark.e2e


class FakeChannel:
    def __init__(self):
        self.acked = False

    def basic_ack(self, delivery_tag):
        self.acked = True


class FakeMethod:
    delivery_tag = 1


def test_notification_consumer_processes_reward_event():
    sender = InMemoryNotificationSender()
    use_case = NotifyRewardProcessedUseCase(sender)
    consumer = RabbitNotificationConsumer(use_case)

    channel = FakeChannel()
    body = b'{"customer_id":"C001","points":10,"cashback":1.0}'

    consumer._on_message(channel, FakeMethod(), None, body)

    assert channel.acked is True
    assert len(sender.sent) == 1
    assert sender.sent[0].customer_id == "C001"
