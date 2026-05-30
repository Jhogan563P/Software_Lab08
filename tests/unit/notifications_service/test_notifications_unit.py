"""
Unit tests – NotificationsService
Scope: domain entity, in-memory sender, use case.
Marker: unit
"""
import pytest
from datetime import UTC, datetime

from app.services.notifications_service.domain.entities import Notification
from app.services.notifications_service.domain.ports import NotificationSender
from app.services.notifications_service.infrastructure.delivery.in_memory import (
    InMemoryNotificationSender,
)
from app.services.notifications_service.application.use_cases import (
    NotifyRewardProcessedUseCase,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Domain entity – Notification
# ---------------------------------------------------------------------------

class TestNotificationEntity:
    def test_fields_stored_correctly(self):
        n = Notification(
            customer_id="C1",
            channel="email",
            message="Tu recompensa: 10 puntos",
        )
        assert n.customer_id == "C1"
        assert n.channel == "email"
        assert n.message == "Tu recompensa: 10 puntos"

    def test_sent_at_defaults_to_none(self):
        n = Notification(customer_id="C1", channel="email", message="msg")
        assert n.sent_at is None

    def test_sent_at_can_be_set(self):
        ts = datetime.now(UTC)
        n = Notification(customer_id="C1", channel="email", message="msg", sent_at=ts)
        assert n.sent_at == ts


# ---------------------------------------------------------------------------
# InMemoryNotificationSender
# ---------------------------------------------------------------------------

class TestInMemoryNotificationSender:
    def setup_method(self):
        self.sender = InMemoryNotificationSender()

    def test_send_appends_notification(self):
        n = Notification(customer_id="C1", channel="email", message="Hola")
        self.sender.send(n)
        assert len(self.sender.sent) == 1
        assert self.sender.sent[0] is n

    def test_send_multiple_are_all_stored(self):
        for i in range(4):
            self.sender.send(Notification(customer_id=f"C{i}", channel="email", message=f"msg{i}"))
        assert len(self.sender.sent) == 4

    def test_sent_list_starts_empty(self):
        assert self.sender.sent == []

    def test_send_preserves_order(self):
        ids = ["C1", "C2", "C3"]
        for cid in ids:
            self.sender.send(Notification(customer_id=cid, channel="email", message="m"))
        assert [n.customer_id for n in self.sender.sent] == ids


# ---------------------------------------------------------------------------
# NotifyRewardProcessedUseCase
# ---------------------------------------------------------------------------

class TestNotifyRewardProcessedUseCase:
    def setup_method(self):
        self.sender = InMemoryNotificationSender()
        self.use_case = NotifyRewardProcessedUseCase(self.sender)

    def test_execute_returns_notification(self):
        result = self.use_case.execute("C1", points=10, cashback=1.0)
        assert isinstance(result, Notification)

    def test_execute_sends_exactly_one_notification(self):
        self.use_case.execute("C1", points=5, cashback=0.5)
        assert len(self.sender.sent) == 1

    def test_execute_notification_channel_is_email(self):
        result = self.use_case.execute("C1", points=5, cashback=0.5)
        assert result.channel == "email"

    def test_execute_message_contains_points(self):
        result = self.use_case.execute("C1", points=42, cashback=4.2)
        assert "42" in result.message

    def test_execute_message_contains_cashback(self):
        result = self.use_case.execute("C1", points=10, cashback=9.99)
        assert "9.99" in result.message

    def test_execute_notification_has_customer_id(self):
        result = self.use_case.execute("CUST-007", points=1, cashback=0.1)
        assert result.customer_id == "CUST-007"

    def test_execute_sent_at_is_not_none(self):
        before = datetime.now(UTC)
        result = self.use_case.execute("C1", points=1, cashback=0.1)
        assert result.sent_at is not None
        assert result.sent_at >= before

    def test_execute_zero_points_and_cashback(self):
        result = self.use_case.execute("C1", points=0, cashback=0.0)
        assert "0" in result.message
