"""
Unit tests – RewardsService
Scope: domain entity, in-memory repo, use case (calculate + execute).
Marker: unit
"""
import pytest
from datetime import UTC, datetime

from app.services.rewards_service.domain.entities import RewardAccount
from app.services.rewards_service.infrastructure.repository.in_memory import (
    InMemoryRewardRepository,
)
from app.services.rewards_service.application.use_cases import ProcessRewardUseCase

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Domain entity – RewardAccount
# ---------------------------------------------------------------------------

class TestRewardAccountEntity:
    def test_default_points_and_cashback_are_zero(self):
        acc = RewardAccount(customer_id="C1")
        assert acc.points == 0
        assert acc.cashback == 0.0

    def test_updated_at_defaults_to_none(self):
        acc = RewardAccount(customer_id="C1")
        assert acc.updated_at is None

    def test_accumulate_points_mutates_in_place(self):
        acc = RewardAccount(customer_id="C1", points=10)
        acc.points += 5
        assert acc.points == 15


# ---------------------------------------------------------------------------
# InMemoryRewardRepository
# ---------------------------------------------------------------------------

class TestInMemoryRewardRepository:
    def setup_method(self):
        self.repo = InMemoryRewardRepository()

    def test_save_and_get_returns_same_account(self):
        acc = RewardAccount(customer_id="C1", points=50)
        self.repo.save(acc)
        assert self.repo.get("C1") == acc

    def test_get_missing_returns_none(self):
        assert self.repo.get("NONE") is None

    def test_save_twice_overwrites(self):
        acc1 = RewardAccount(customer_id="C1", points=10)
        acc2 = RewardAccount(customer_id="C1", points=999)
        self.repo.save(acc1)
        self.repo.save(acc2)
        assert self.repo.get("C1").points == 999

    def test_multiple_accounts_independent(self):
        for i in range(3):
            self.repo.save(RewardAccount(customer_id=f"C{i}", points=i * 10))
        assert self.repo.get("C0").points == 0
        assert self.repo.get("C1").points == 10
        assert self.repo.get("C2").points == 20


# ---------------------------------------------------------------------------
# ProcessRewardUseCase.calculate
# ---------------------------------------------------------------------------

class TestCalculate:
    def setup_method(self):
        self.uc = ProcessRewardUseCase(InMemoryRewardRepository())

    @pytest.mark.parametrize("amount,expected_points,expected_cashback", [
        (100.0, 10, 1.0),
        (250.0, 25, 2.5),
        (9.99,   0, 0.10),   # menos de 10 → 0 puntos
        (0.0,    0, 0.0),
        (1000.0, 100, 10.0),
    ])
    def test_calculate_parametrized(self, amount, expected_points, expected_cashback):
        points, cashback = self.uc.calculate(amount)
        assert points == expected_points
        assert round(cashback, 2) == expected_cashback

    def test_calculate_does_not_use_repository(self):
        """calculate() es puro: no toca el repo."""
        repo = InMemoryRewardRepository()
        uc = ProcessRewardUseCase(repo)
        uc.calculate(500.0)
        # nada guardado
        assert repo.get("any") is None


# ---------------------------------------------------------------------------
# ProcessRewardUseCase.execute
# ---------------------------------------------------------------------------

class TestProcessRewardExecute:
    def _make_payload(self, amount: float = 120.0, card: str = "1234567890123456") -> dict:
        return {"amount": amount, "card_number": card}

    def setup_method(self):
        self.repo = InMemoryRewardRepository()
        self.uc = ProcessRewardUseCase(self.repo)

    def test_execute_creates_new_account(self):
        result = self.uc.execute(self._make_payload())
        assert result.customer_id == "3456"   # últimos 4 dígitos
        assert result.points == 12
        assert round(result.cashback, 2) == 1.2

    def test_execute_persists_account(self):
        result = self.uc.execute(self._make_payload())
        stored = self.repo.get(result.customer_id)
        assert stored is not None

    def test_execute_accumulates_on_second_call(self):
        payload = self._make_payload(amount=100.0, card="0000000000001111")
        self.uc.execute(payload)
        self.uc.execute(payload)
        acc = self.repo.get("1111")
        assert acc.points == 20        # 10 + 10
        assert round(acc.cashback, 2) == 2.0

    def test_execute_sets_updated_at(self):
        before = datetime.now(UTC)
        result = self.uc.execute(self._make_payload())
        assert result.updated_at is not None
        assert result.updated_at >= before

    def test_execute_customer_id_is_last_4_digits(self):
        result = self.uc.execute({"amount": 10.0, "card_number": "9999888877776666"})
        assert result.customer_id == "6666"
