"""
Unit tests – CustomerService
Scope: domain entity + use case con repositorio in-memory fake.
Marker: unit
"""
import pytest

from app.services.customer_service.domain.entities import Customer
from app.services.customer_service.infrastructure.repository.in_memory import (
    InMemoryCustomerRepository,
)
from app.services.customer_service.application.use_cases import RegisterCustomerUseCase

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Domain entity
# ---------------------------------------------------------------------------

class TestCustomerEntity:
    def test_customer_fields_stored_correctly(self):
        c = Customer(customer_id="C1", name="Ana López", email="ana@mail.com")
        assert c.customer_id == "C1"
        assert c.name == "Ana López"
        assert c.email == "ana@mail.com"

    def test_two_customers_with_same_id_are_equal(self):
        c1 = Customer(customer_id="C1", name="Ana", email="ana@mail.com")
        c2 = Customer(customer_id="C1", name="Ana", email="ana@mail.com")
        assert c1 == c2

    def test_customers_with_different_ids_differ(self):
        c1 = Customer(customer_id="C1", name="Ana", email="ana@mail.com")
        c2 = Customer(customer_id="C2", name="Ana", email="ana@mail.com")
        assert c1 != c2


# ---------------------------------------------------------------------------
# InMemoryCustomerRepository
# ---------------------------------------------------------------------------

class TestInMemoryCustomerRepository:
    def setup_method(self):
        self.repo = InMemoryCustomerRepository()

    def test_save_and_get_returns_same_customer(self):
        c = Customer(customer_id="C10", name="Luis", email="luis@mail.com")
        self.repo.save(c)
        result = self.repo.get("C10")
        assert result == c

    def test_get_nonexistent_returns_none(self):
        assert self.repo.get("NONEXISTENT") is None

    def test_save_overwrites_existing_entry(self):
        c1 = Customer(customer_id="C10", name="Luis", email="luis@mail.com")
        c2 = Customer(customer_id="C10", name="Luis Actualizado", email="luis2@mail.com")
        self.repo.save(c1)
        self.repo.save(c2)
        assert self.repo.get("C10").name == "Luis Actualizado"

    def test_multiple_customers_stored_independently(self):
        for i in range(5):
            self.repo.save(Customer(customer_id=f"C{i}", name=f"User{i}", email=f"u{i}@mail.com"))
        for i in range(5):
            assert self.repo.get(f"C{i}") is not None


# ---------------------------------------------------------------------------
# RegisterCustomerUseCase
# ---------------------------------------------------------------------------

class TestRegisterCustomerUseCase:
    def setup_method(self):
        self.repo = InMemoryCustomerRepository()
        self.use_case = RegisterCustomerUseCase(self.repo)

    def test_execute_returns_customer_with_correct_data(self):
        customer = self.use_case.execute("C99", "María", "maria@mail.com")
        assert customer.customer_id == "C99"
        assert customer.name == "María"
        assert customer.email == "maria@mail.com"

    def test_execute_persists_customer_in_repository(self):
        self.use_case.execute("C99", "María", "maria@mail.com")
        stored = self.repo.get("C99")
        assert stored is not None
        assert stored.name == "María"

    def test_execute_successive_calls_stored_independently(self):
        self.use_case.execute("A1", "Alice", "alice@mail.com")
        self.use_case.execute("B1", "Bob", "bob@mail.com")
        assert self.repo.get("A1").name == "Alice"
        assert self.repo.get("B1").name == "Bob"

    def test_execute_overwrite_same_id(self):
        self.use_case.execute("C99", "María", "maria@mail.com")
        self.use_case.execute("C99", "María Actualizada", "nueva@mail.com")
        assert self.repo.get("C99").name == "María Actualizada"
