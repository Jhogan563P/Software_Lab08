import pytest
from unittest.mock import MagicMock

from app.shared.messaging.base import BaseRabbitConsumer, BaseRabbitPublisher

pytestmark = pytest.mark.unit


class DummyPublisher(BaseRabbitPublisher[dict]):
    def _serialize(self, message: dict) -> str:
        return str(message)


class DummyConsumer(BaseRabbitConsumer[dict]):
    def __init__(self, conn_factory):
        super().__init__(connection_factory=conn_factory, queue="q1")
        self.handled = []

    def _deserialize(self, body: bytes) -> dict:
        return {"deserialized": body.decode()}

    def _handle(self, payload: dict) -> None:
        self.handled.append(payload)


def test_base_rabbit_publisher_closes_connection_on_publish_error():
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_channel.basic_publish.side_effect = Exception("publish failed")
    mock_conn.channel.return_value = mock_channel

    pub = DummyPublisher(connection_factory=lambda: mock_conn, queue="q1", exchange="e1")

    with pytest.raises(Exception, match="publish failed"):
        pub.publish({"hello": "world"})

    mock_conn.close.assert_called_once()


def test_base_rabbit_consumer_on_message_acks_after_handle():
    consumer = DummyConsumer(lambda: MagicMock())
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 1

    consumer._on_message(mock_channel, mock_method, None, b"body")

    assert consumer.handled == [{"deserialized": "body"}]
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)


def test_base_rabbit_consumer_on_message_propagates_handle_errors():
    consumer = DummyConsumer(lambda: MagicMock())
    consumer._handle = MagicMock(side_effect=Exception("Failed"))

    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 1

    with pytest.raises(Exception, match="Failed"):
        consumer._on_message(mock_channel, mock_method, None, b"body")