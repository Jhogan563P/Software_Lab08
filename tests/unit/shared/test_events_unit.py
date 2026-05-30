from datetime import UTC, datetime

import pytest

from app.shared.messaging.events import DinnerRegisteredEvent, RewardProcessedEvent

pytestmark = pytest.mark.unit


def test_dinner_registered_event_fields_are_stored():
    timestamp = datetime(2026, 5, 30, 12, 0, 0, tzinfo=UTC)
    event = DinnerRegisteredEvent(
        amount=80.0,
        card_number="4111111111111111",
        restaurant_id="R1",
        timestamp=timestamp,
    )

    assert event.amount == 80.0
    assert event.card_number == "4111111111111111"
    assert event.restaurant_id == "R1"
    assert event.timestamp == timestamp


def test_reward_processed_event_equality_and_fields():
    timestamp = datetime(2026, 5, 30, 13, 0, 0, tzinfo=UTC)
    event_one = RewardProcessedEvent(
        customer_id="C1",
        points=12,
        cashback=1.2,
        processed_at=timestamp,
    )
    event_two = RewardProcessedEvent(
        customer_id="C1",
        points=12,
        cashback=1.2,
        processed_at=timestamp,
    )

    assert event_one == event_two
    assert event_one.customer_id == "C1"
    assert event_one.points == 12
    assert event_one.cashback == 1.2
    assert event_one.processed_at == timestamp