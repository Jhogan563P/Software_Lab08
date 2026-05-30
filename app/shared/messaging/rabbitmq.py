import json

import pika

from app.shared.config.settings import AppSettings


class RabbitConnectionFactory:
    def __init__(self, settings: AppSettings | None = None):
        self.settings = settings or AppSettings()

    def create_parameters(self) -> pika.ConnectionParameters:
        credentials = pika.PlainCredentials(
            self.settings.rabbit.username,
            self.settings.rabbit.password,
        )
        return pika.ConnectionParameters(
            self.settings.rabbit.host,
            self.settings.rabbit.port,
            self.settings.rabbit.vhost,
            credentials,
        )

    def create_connection(self) -> pika.BlockingConnection:
        return pika.BlockingConnection(self.create_parameters())

    @staticmethod
    def dumps(message: dict) -> str:
        return json.dumps(message)
