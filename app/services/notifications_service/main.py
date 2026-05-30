from app.services.notifications_service.application.use_cases import NotifyRewardProcessedUseCase
from app.services.notifications_service.infrastructure.delivery.in_memory import InMemoryNotificationSender
from app.services.notifications_service.infrastructure.messaging.consumer import RabbitNotificationConsumer


def main() -> None:
    sender = InMemoryNotificationSender()
    notification_use_case = NotifyRewardProcessedUseCase(sender)
    consumer = RabbitNotificationConsumer(notification_use_case)
    consumer.start()


if __name__ == "__main__":
    main()
