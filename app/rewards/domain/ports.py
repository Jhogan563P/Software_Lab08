from abc import ABC, abstractmethod
from app.rewards.domain.entities import RewardAccount


class RewardRepository(ABC):
    @abstractmethod
    def save(self, account: RewardAccount) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get(self, customer_id: str) -> RewardAccount | None:
        raise NotImplementedError()
