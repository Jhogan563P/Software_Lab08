from abc import ABC, abstractmethod

from app.services.dinner_service.domain.entities import DinnerTransaction


class DinnerPublisher(ABC):
    @abstractmethod
    def publish_dinner(self, dinner: DinnerTransaction) -> None:
        raise NotImplementedError()
