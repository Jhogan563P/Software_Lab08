from datetime import UTC, datetime

from app.services.rewards_service.domain.entities import RewardAccount
from app.services.rewards_service.domain.ports import RewardRepository
from typing import Optional


# lazy import of customer store to avoid circular imports at module import time
def _ensure_customer_exists(customer_id: str) -> None:
    try:
        from app.services.customer_service.store import customer_repository
        from app.services.customer_service.domain.entities import Customer
    except Exception:
        return

    if customer_repository.get(customer_id) is None:
        customer = Customer(customer_id=customer_id, name="unknown", email=f"{customer_id}@example.com")
        customer_repository.save(customer)


class ProcessRewardUseCase:
    def __init__(self, repository: RewardRepository):
        self.repository = repository

    def calculate(self, amount: float) -> tuple[int, float]:
        points = int(amount // 10)
        cashback = round(amount * 0.01, 2)
        return points, cashback

    def execute(self, payload: dict) -> RewardAccount:
        amount = float(payload.get("amount", 0))
        customer_id = payload.get("card_number")[-4:]
        points, cashback = self.calculate(amount)
        existing = self.repository.get(customer_id)
        account = existing or RewardAccount(customer_id=customer_id)
        account.points += points
        account.cashback += cashback
        account.updated_at = datetime.now(UTC)
        self.repository.save(account)
        # if the account was newly created, ensure a customer record exists
        if existing is None:
            _ensure_customer_exists(customer_id)
        return account
