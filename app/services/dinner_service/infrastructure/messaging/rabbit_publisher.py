import json
from typing import Callable, Optional

import pika

from app.services.dinner_service.application.use_cases import RegisterDinnerUseCase
from app.services.dinner_service.domain.entities import DinnerTransaction
from app.services.dinner_service.domain.ports import DinnerPublisher
from app.shared.config.settings import AppSettings
from app.shared.messaging.base import BaseRabbitPublisher
from app.shared.messaging.rabbitmq import RabbitConnectionFactory


class RabbitDinnerPublisher(BaseRabbitPublisher[DinnerTransaction], DinnerPublisher):
    def __init__(
        self,
        connection_factory: Optional[Callable[[], pika.BlockingConnection]] = None,
        settings: AppSettings | None = None,
        queue_name: str = "laboratorio_1",
    ) -> None:
        settings = settings or AppSettings()
        if connection_factory is None:
            factory = RabbitConnectionFactory(settings)
            connection_factory = factory.create_connection
        super().__init__(connection_factory=connection_factory, queue=queue_name, exchange="")

    def _serialize(self, dinner: DinnerTransaction) -> str:
        return json.dumps(
            {
                "amount": dinner.amount,
                "card_number": dinner.card_number,
                "restaurant_id": dinner.restaurant_id,
                "timestamp": dinner.timestamp.isoformat(),
            }
        )

    def publish_dinner(self, dinner: DinnerTransaction) -> None:
        self.publish(dinner)
