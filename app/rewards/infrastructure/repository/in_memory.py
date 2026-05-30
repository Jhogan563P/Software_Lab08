from app.rewards.domain.entities import RewardAccount
from app.rewards.domain.ports import RewardRepository


class InMemoryRewardRepository(RewardRepository):
    def __init__(self):
        self._items: dict[str, RewardAccount] = {}

    def save(self, account: RewardAccount) -> None:
        self._items[account.customer_id] = account

    def get(self, customer_id: str) -> RewardAccount | None:
        return self._items.get(customer_id)
