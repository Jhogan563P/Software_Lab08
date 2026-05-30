from datetime import UTC, datetime

import pytest

from app.services.customer_service.domain.entities import Customer
from app.services.customer_service.domain.ports import CustomerRepository
from app.services.dinner_service.domain.entities import DinnerTransaction
from app.services.dinner_service.domain.ports import DinnerPublisher
from app.services.notifications_service.domain.entities import Notification
from app.services.notifications_service.domain.ports import NotificationSender
from app.services.rewards_service.domain.entities import RewardAccount
from app.services.rewards_service.domain.ports import RewardRepository

pytestmark = pytest.mark.unit


class DummyCustomerRepository(CustomerRepository):
    def save(self, customer: Customer) -> None:
        return super().save(customer)

    def get(self, customer_id: str) -> Customer | None:
        return super().get(customer_id)


class DummyRewardRepository(RewardRepository):
    def save(self, account: RewardAccount) -> None:
        return super().save(account)

    def get(self, customer_id: str) -> RewardAccount | None:
        return super().get(customer_id)


class DummyNotificationSender(NotificationSender):
    def send(self, notification: Notification) -> None:
        return super().send(notification)


class DummyDinnerPublisher(DinnerPublisher):
    def publish_dinner(self, dinner: DinnerTransaction) -> None:
        return super().publish_dinner(dinner)


def test_customer_repository_contract_raises_not_implemented():
    repo = DummyCustomerRepository()

    with pytest.raises(NotImplementedError):
        repo.save(Customer(customer_id="C1", name="Ana", email="ana@mail.com"))

    with pytest.raises(NotImplementedError):
        repo.get("C1")


def test_reward_repository_contract_raises_not_implemented():
    repo = DummyRewardRepository()

    with pytest.raises(NotImplementedError):
        repo.save(RewardAccount(customer_id="C1"))

    with pytest.raises(NotImplementedError):
        repo.get("C1")


def test_notification_sender_contract_raises_not_implemented():
    sender = DummyNotificationSender()

    with pytest.raises(NotImplementedError):
        sender.send(Notification(customer_id="C1", channel="email", message="hola"))


def test_dinner_publisher_contract_raises_not_implemented():
    publisher = DummyDinnerPublisher()

    with pytest.raises(NotImplementedError):
        publisher.publish_dinner(
            DinnerTransaction(
                amount=10.0,
                card_number="4111111111111111",
                restaurant_id="R1",
                timestamp=datetime(2026, 5, 30, 14, 0, 0, tzinfo=UTC),
            )
        )