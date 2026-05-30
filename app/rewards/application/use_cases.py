from datetime import UTC, datetime
from app.rewards.domain.entities import RewardAccount
from app.rewards.domain.ports import RewardRepository


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
        account = self.repository.get(customer_id) or RewardAccount(customer_id=customer_id)
        account.points += points
        account.cashback += cashback
        account.updated_at = datetime.now(UTC)
        self.repository.save(account)
        return account
