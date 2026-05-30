from app.notifications.application.use_cases import NotifyRewardProcessedUseCase
from app.notifications.infrastructure.delivery.in_memory import InMemoryNotificationSender
from app.rewards.application.use_cases import ProcessRewardUseCase
from app.rewards.infrastructure.messaging.consumer import RabbitRewardConsumer
from app.rewards.infrastructure.repository.in_memory import InMemoryRewardRepository


def main() -> None:
    repo = InMemoryRewardRepository()
    reward_uc = ProcessRewardUseCase(repo)
    sender = InMemoryNotificationSender()
    notification_uc = NotifyRewardProcessedUseCase(sender)
    consumer = RabbitRewardConsumer(reward_uc, notification_uc)
    consumer.start()


if __name__ == "__main__":
    main()
