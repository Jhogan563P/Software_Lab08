from abc import ABC, abstractmethod
from app.customer.domain.entities import Customer


class CustomerRepository(ABC):
    @abstractmethod
    def save(self, customer: Customer) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get(self, customer_id: str) -> Customer | None:
        raise NotImplementedError()
