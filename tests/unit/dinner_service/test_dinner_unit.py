"""
Unit tests – DinnerService
Scope: domain entity + use case con fake publisher.
Marker: unit
"""
from datetime import UTC, datetime

import pytest

from app.services.dinner_service.domain.entities import DinnerTransaction
from app.services.dinner_service.domain.ports import DinnerPublisher
from app.services.dinner_service.application.use_cases import RegisterDinnerUseCase

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Fake / stub
# ---------------------------------------------------------------------------

class FakeDinnerPublisher(DinnerPublisher):
    def __init__(self):
        self.published: list[DinnerTransaction] = []

    def publish_dinner(self, dinner: DinnerTransaction) -> None:
        self.published.append(dinner)


# ---------------------------------------------------------------------------
# Domain entity
# ---------------------------------------------------------------------------

class TestDinnerTransactionEntity:
    def _make_tx(self, amount=50.0, card="4111111111111111", restaurant="R1"):
        return DinnerTransaction(
            amount=amount,
            card_number=card,
            restaurant_id=restaurant,
            timestamp=datetime.now(UTC),
        )

    def test_entity_fields_stored_correctly(self):
        tx = self._make_tx()
        assert tx.amount == 50.0
        assert tx.card_number == "4111111111111111"
        assert tx.restaurant_id == "R1"

    def test_entity_is_frozen(self):
        """DinnerTransaction es frozen=True: intentar modificar lanza FrozenInstanceError."""
        tx = self._make_tx()
        with pytest.raises(Exception):
            tx.amount = 999.0  # type: ignore[misc]

    def test_entity_equality_same_values(self):
        ts = datetime(2026, 1, 1, tzinfo=UTC)
        t1 = DinnerTransaction(amount=10.0, card_number="1234", restaurant_id="R1", timestamp=ts)
        t2 = DinnerTransaction(amount=10.0, card_number="1234", restaurant_id="R1", timestamp=ts)
        assert t1 == t2


# ---------------------------------------------------------------------------
# RegisterDinnerUseCase
# ---------------------------------------------------------------------------

class TestRegisterDinnerUseCase:
    def setup_method(self):
        self.publisher = FakeDinnerPublisher()
        self.use_case = RegisterDinnerUseCase(self.publisher)

    def _make_tx(self, amount=100.0):
        return DinnerTransaction(
            amount=amount,
            card_number="4111111111111111",
            restaurant_id="R1",
            timestamp=datetime.now(UTC),
        )

    def test_execute_returns_same_transaction(self):
        tx = self._make_tx()
        result = self.use_case.execute(tx)
        assert result is tx

    def test_execute_calls_publisher_once(self):
        tx = self._make_tx()
        self.use_case.execute(tx)
        assert len(self.publisher.published) == 1

    def test_execute_publishes_correct_transaction(self):
        tx = self._make_tx(amount=250.0)
        self.use_case.execute(tx)
        assert self.publisher.published[0].amount == 250.0

    def test_execute_multiple_transactions_all_published(self):
        for amount in [10.0, 20.0, 30.0]:
            self.use_case.execute(self._make_tx(amount))
        assert len(self.publisher.published) == 3

    def test_execute_does_not_modify_transaction(self):
        tx = self._make_tx(amount=99.0)
        result = self.use_case.execute(tx)
        assert result.amount == 99.0
        assert result.card_number == "4111111111111111"
