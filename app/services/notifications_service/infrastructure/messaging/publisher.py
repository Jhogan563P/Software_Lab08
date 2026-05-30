import json
from typing import Callable, Optional

import pika

from app.shared.messaging.base import BaseRabbitPublisher
from app.shared.messaging.rabbitmq import RabbitConnectionFactory


class RabbitRewardProcessedPublisher(BaseRabbitPublisher[dict]):
    def __init__(
        self,
        connection_factory: Optional[Callable[[], pika.BlockingConnection]] = None,
        queue_name: str = "rewards_processed",
    ):
        self.queue_name = queue_name
        if connection_factory is None:
            connection_factory = RabbitConnectionFactory().create_connection
        super().__init__(connection_factory=connection_factory, queue=queue_name, exchange="")

    def _serialize(self, payload: dict) -> str:
        return json.dumps(payload)
