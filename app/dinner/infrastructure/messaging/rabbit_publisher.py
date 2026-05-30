import json
import pika
from app.dinner.domain.entities import DinnerTransaction
from app.dinner.domain.ports import DinnerPublisher
from app.shared.config.settings import AppSettings


class RabbitDinnerPublisher(DinnerPublisher):
    def __init__(self, settings: AppSettings | None = None, queue_name: str = "laboratorio_1"):
        self.settings = settings or AppSettings()
        self.queue_name = queue_name

    def publish_dinner(self, dinner: DinnerTransaction) -> None:
        credentials = pika.PlainCredentials(
            self.settings.rabbit.username,
            self.settings.rabbit.password,
        )
        params = pika.ConnectionParameters(
            self.settings.rabbit.host,
            self.settings.rabbit.port,
            self.settings.rabbit.vhost,
            credentials,
        )
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=json.dumps({
                "amount": dinner.amount,
                "card_number": dinner.card_number,
                "restaurant_id": dinner.restaurant_id,
                "timestamp": dinner.timestamp.isoformat(),
            }),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
