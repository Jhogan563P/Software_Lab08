from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

import pika

T = TypeVar("T")


class BaseRabbitPublisher(ABC, Generic[T]):
    def __init__(
        self,
        connection_factory: Callable[[], pika.BlockingConnection],
        queue: str,
        exchange: str = "",
    ) -> None:
        self._connection_factory = connection_factory
        self._queue = queue
        self._exchange = exchange

    def publish(self, message: T) -> None:
        payload = self._serialize(message).encode("utf-8")
        connection = self._connection_factory()
        try:
            channel = connection.channel()
            channel.queue_declare(queue=self._queue, durable=True)
            channel.basic_publish(
                exchange=self._exchange,
                routing_key=self._queue,
                body=payload,
                properties=pika.BasicProperties(delivery_mode=2),
            )
        finally:
            connection.close()

    @abstractmethod
    def _serialize(self, message: T) -> str:
        raise NotImplementedError


class BaseRabbitConsumer(ABC, Generic[T]):
    def __init__(
        self,
        connection_factory: Callable[[], pika.BlockingConnection],
        queue: str,
        prefetch_count: int = 1,
    ) -> None:
        self._connection_factory = connection_factory
        self._queue = queue
        self._prefetch_count = prefetch_count

    def start(self) -> None:
        connection = self._connection_factory()
        try:
            channel = connection.channel()
            channel.queue_declare(queue=self._queue, durable=True)
            channel.basic_qos(prefetch_count=self._prefetch_count)
            channel.basic_consume(
                queue=self._queue,
                on_message_callback=self._on_message,
                auto_ack=False,
            )
            channel.start_consuming()
        finally:
            if connection and connection.is_open:
                connection.close()

    def _on_message(self, channel, method, _properties, body: bytes) -> None:
        message = self._deserialize(body)
        self._handle(message)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    @abstractmethod
    def _deserialize(self, body: bytes) -> T:
        raise NotImplementedError

    @abstractmethod
    def _handle(self, message: T) -> None:
        raise NotImplementedError
