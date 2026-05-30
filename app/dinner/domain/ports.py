from abc import ABC, abstractmethod
from app.dinner.domain.entities import DinnerTransaction


class DinnerPublisher(ABC):
    @abstractmethod
    def publish_dinner(self, dinner: DinnerTransaction) -> None:
        raise NotImplementedError()
