from app.customer.domain.entities import Customer
from app.customer.domain.ports import CustomerRepository


class RegisterCustomerUseCase:
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    def execute(self, customer_id: str, name: str, email: str) -> Customer:
        customer = Customer(customer_id=customer_id, name=name, email=email)
        self.repository.save(customer)
        return customer
