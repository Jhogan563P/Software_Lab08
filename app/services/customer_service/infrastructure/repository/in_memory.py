from app.services.customer_service.domain.entities import Customer
from app.services.customer_service.domain.ports import CustomerRepository


class InMemoryCustomerRepository(CustomerRepository):
    def __init__(self):
        self._items: dict[str, Customer] = {}

    def save(self, customer: Customer) -> None:
        self._items[customer.customer_id] = customer

    def get(self, customer_id: str) -> Customer | None:
        return self._items.get(customer_id)
