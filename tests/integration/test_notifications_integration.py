"""
Integration tests – NotificationsService
Scope: use case con InMemoryNotificationSender + consumer _handle vía mensaje fake.
Marker: integration
"""
import json
import pytest

from app.services.notifications_service.application.use_cases import (
    NotifyRewardProcessedUseCase,
)
from app.services.notifications_service.infrastructure.delivery.in_memory import (
    InMemoryNotificationSender,
)
from app.services.notifications_service.infrastructure.messaging.consumer import (
    RabbitNotificationConsumer,
)

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sender():
    return InMemoryNotificationSender()


@pytest.fixture()
def use_case(sender):
    return NotifyRewardProcessedUseCase(sender)


@pytest.fixture()
def consumer(use_case):
    return RabbitNotificationConsumer(use_case)


class FakeChannel:
    def __init__(self):
        self.acked = False

    def basic_ack(self, delivery_tag):
        self.acked = True


class FakeMethod:
    delivery_tag = 1


# ---------------------------------------------------------------------------
# Tests vía use case directo
# ---------------------------------------------------------------------------

class TestNotifyRewardIntegration:
    def test_execute_persists_in_sender(self, use_case, sender):
        use_case.execute(customer_id="C1", points=10, cashback=1.0)
        assert len(sender.sent) == 1

    def test_execute_customer_id_matches(self, use_case, sender):
        use_case.execute(customer_id="C99", points=5, cashback=0.5)
        assert sender.sent[0].customer_id == "C99"

    def test_execute_message_has_points_and_cashback(self, use_case, sender):
        use_case.execute(customer_id="C1", points=15, cashback=3.75)
        msg = sender.sent[0].message
        assert "15" in msg
        assert "3.75" in msg

    def test_execute_multiple_notifications_accumulate(self, use_case, sender):
        use_case.execute("C1", 10, 1.0)
        use_case.execute("C2", 20, 2.0)
        assert len(sender.sent) == 2
        assert sender.sent[0].customer_id == "C1"
        assert sender.sent[1].customer_id == "C2"


# ---------------------------------------------------------------------------
# Tests vía consumer (simula mensaje entrante de RabbitMQ)
# ---------------------------------------------------------------------------

class TestNotificationConsumerIntegration:
    def _send(self, consumer, payload: dict):
        body = json.dumps(payload).encode()
        consumer._on_message(FakeChannel(), FakeMethod(), None, body)

    def test_consumer_acks_message(self, consumer, sender):
        ch = FakeChannel()
        body = json.dumps({"customer_id": "C1", "points": 10, "cashback": 1.0}).encode()
        consumer._on_message(ch, FakeMethod(), None, body)
        assert ch.acked is True

    def test_consumer_calls_use_case(self, consumer, sender):
        self._send(consumer, {"customer_id": "C1", "points": 10, "cashback": 1.0})
        assert len(sender.sent) == 1

    def test_consumer_correct_customer_id(self, consumer, sender):
        self._send(consumer, {"customer_id": "XYZ", "points": 5, "cashback": 0.5})
        assert sender.sent[0].customer_id == "XYZ"

    def test_consumer_handles_zero_points(self, consumer, sender):
        self._send(consumer, {"customer_id": "C2", "points": 0, "cashback": 0.0})
        assert len(sender.sent) == 1

    def test_consumer_multiple_messages(self, consumer, sender):
        for i in range(3):
            self._send(consumer, {"customer_id": f"C{i}", "points": i, "cashback": float(i)})
        assert len(sender.sent) == 3
