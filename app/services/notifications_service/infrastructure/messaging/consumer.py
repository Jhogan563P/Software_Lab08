import json

from app.services.notifications_service.application.use_cases import NotifyRewardProcessedUseCase
from app.shared.messaging.base import BaseRabbitConsumer
from app.shared.messaging.rabbitmq import RabbitConnectionFactory


class RabbitNotificationConsumer(BaseRabbitConsumer[dict]):
    def __init__(self, notification_use_case: NotifyRewardProcessedUseCase, queue_name: str = "rewards_processed"):
        self.notification_use_case = notification_use_case
        connection_factory = RabbitConnectionFactory().create_connection
        super().__init__(connection_factory=connection_factory, queue=queue_name)

    def _deserialize(self, body: bytes) -> dict:
        return json.loads(body.decode())

    def _handle(self, payload: dict) -> None:
        self.notification_use_case.execute(
            customer_id=payload["customer_id"],
            points=payload["points"],
            cashback=payload["cashback"],
        )
