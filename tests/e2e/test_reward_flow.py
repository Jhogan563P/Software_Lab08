from datetime import UTC, datetime

from app.dinner.application.use_cases import RegisterDinnerUseCase
from app.dinner.domain.entities import DinnerTransaction
from app.notifications.application.use_cases import NotifyRewardProcessedUseCase
from app.notifications.infrastructure.delivery.in_memory import InMemoryNotificationSender
from app.rewards.application.use_cases import ProcessRewardUseCase
from app.rewards.infrastructure.repository.in_memory import InMemoryRewardRepository


class FakeDinnerPublisher:
    def __init__(self):
        self.messages = []

    def publish_dinner(self, dinner):
        self.messages.append(dinner)


def test_end_to_end_reward_and_notification_flow():
    dinner_publisher = FakeDinnerPublisher()
    dinner_uc = RegisterDinnerUseCase(dinner_publisher)
    rewards_repo = InMemoryRewardRepository()
    rewards_uc = ProcessRewardUseCase(rewards_repo)
    notification_sender = InMemoryNotificationSender()
    notification_uc = NotifyRewardProcessedUseCase(notification_sender)

    dinner = DinnerTransaction(
        amount=100.0,
        card_number="4111111111111111",
        restaurant_id="R1",
        timestamp=datetime.now(UTC),
    )

    dinner_uc.execute(dinner)
    assert len(dinner_publisher.messages) == 1

    reward_account = rewards_uc.execute({
        "amount": dinner.amount,
        "card_number": dinner.card_number,
        "restaurant_id": dinner.restaurant_id,
        "timestamp": dinner.timestamp.isoformat(),
    })

    notification = notification_uc.execute(
        customer_id=reward_account.customer_id,
        points=reward_account.points,
        cashback=reward_account.cashback,
    )

    assert reward_account.points == 10
    assert len(notification_sender.sent) == 1
    assert notification.customer_id == reward_account.customer_id
