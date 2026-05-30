import json

from app.services.notifications_service.infrastructure.messaging.publisher import RabbitRewardProcessedPublisher
from app.services.rewards_service.application.use_cases import ProcessRewardUseCase
from app.shared.messaging.base import BaseRabbitConsumer
from app.shared.messaging.rabbitmq import RabbitConnectionFactory


class RabbitRewardConsumer(BaseRabbitConsumer[dict]):
    def __init__(
        self,
        reward_use_case: ProcessRewardUseCase,
        processed_reward_publisher: RabbitRewardProcessedPublisher | None = None,
        queue_name: str = "laboratorio_1",
    ):
        self.reward_use_case = reward_use_case
        self.processed_reward_publisher = processed_reward_publisher
        connection_factory = RabbitConnectionFactory().create_connection
        super().__init__(connection_factory=connection_factory, queue=queue_name)

    def _deserialize(self, body: bytes) -> dict:
        return json.loads(body.decode())

    def _handle(self, payload: dict) -> None:
        account = self.reward_use_case.execute(payload)

        if self.processed_reward_publisher is not None:
            self.processed_reward_publisher.publish(
                {
                    "customer_id": account.customer_id,
                    "points": account.points,
                    "cashback": account.cashback,
                    "processed_at": account.updated_at.isoformat() if account.updated_at else None,
                }
            )
