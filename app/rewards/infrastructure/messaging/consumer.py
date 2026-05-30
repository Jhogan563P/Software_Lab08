import json

import pika

from app.notifications.application.use_cases import NotifyRewardProcessedUseCase
from app.rewards.application.use_cases import ProcessRewardUseCase
from app.shared.messaging.rabbitmq import RabbitConnectionFactory


class RabbitRewardConsumer:
    def __init__(
        self,
        reward_use_case: ProcessRewardUseCase,
        notification_use_case: NotifyRewardProcessedUseCase | None = None,
        queue_name: str = "laboratorio_1",
    ):
        self.reward_use_case = reward_use_case
        self.notification_use_case = notification_use_case
        self.queue_name = queue_name
        self.connection_factory = RabbitConnectionFactory()

    def _on_message(self, ch, method, properties, body):
        payload = json.loads(body.decode())
        account = self.reward_use_case.execute(payload)

        if self.notification_use_case is not None:
            self.notification_use_case.execute(
                customer_id=account.customer_id,
                points=account.points,
                cashback=account.cashback,
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self) -> None:
        connection = pika.BlockingConnection(self.connection_factory.create_parameters())
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_name, on_message_callback=self._on_message)
        channel.start_consuming()
