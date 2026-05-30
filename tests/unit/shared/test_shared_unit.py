import pytest
from unittest.mock import MagicMock, patch
from app.shared.health import rabbit_healthcheck
from app.shared.messaging.rabbitmq import RabbitConnectionFactory
from app.shared.messaging.base import BaseRabbitPublisher, BaseRabbitConsumer
from app.shared.config.settings import AppSettings, RabbitSettings
from fastapi import HTTPException

pytestmark = pytest.mark.unit


def test_rabbit_healthcheck_success(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.is_open = True
    
    # Mock create_connection to return our mock connection
    monkeypatch.setattr(
        "app.shared.health.RabbitConnectionFactory.create_connection", 
        lambda self: mock_conn
    )
    
    res = rabbit_healthcheck()
    assert res["status"] == "ok"
    mock_conn.close.assert_called_once()


def test_rabbit_healthcheck_failure(monkeypatch):
    def raise_exception():
        raise Exception("Connection failed")
        
    monkeypatch.setattr(
        "app.shared.health.RabbitConnectionFactory.create_connection", 
        lambda self: raise_exception()
    )
    
    with pytest.raises(HTTPException) as excinfo:
        rabbit_healthcheck()
    assert excinfo.value.status_code == 503
    assert "Connection failed" in excinfo.value.detail


def test_rabbit_connection_factory(monkeypatch):
    monkeypatch.setenv("RABBIT_HOST", "my-host")
    settings = AppSettings(rabbit=RabbitSettings(host="my-host"))
    factory = RabbitConnectionFactory(settings)
    assert factory.settings.rabbit.host == "my-host"


class DummyPublisher(BaseRabbitPublisher[dict]):
    def _serialize(self, message: dict) -> str:
        return str(message)


def test_base_rabbit_publisher(monkeypatch):
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_conn.channel.return_value = mock_channel
    
    pub = DummyPublisher(connection_factory=lambda: mock_conn, queue="q1", exchange="e1")
    pub.publish({"hello": "world"})
    
    mock_conn.channel.assert_called_once()
    mock_channel.queue_declare.assert_called_once_with(queue="q1", durable=True)
    mock_channel.basic_publish.assert_called_once()
    mock_conn.close.assert_called_once()


class DummyConsumer(BaseRabbitConsumer[dict]):
    def __init__(self, conn_factory):
        super().__init__(connection_factory=conn_factory, queue="q1")
        self.handled = []
        
    def _deserialize(self, body: bytes) -> dict:
        return {"deserialized": body.decode()}
        
    def _handle(self, payload: dict) -> None:
        self.handled.append(payload)


def test_base_rabbit_consumer(monkeypatch):
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_conn.channel.return_value = mock_channel
    
    consumer = DummyConsumer(lambda: mock_conn)
    consumer.start()
    
    mock_conn.channel.assert_called_once()
    mock_channel.queue_declare.assert_called_once_with(queue="q1", durable=True)
    mock_channel.basic_consume.assert_called_once()
    mock_channel.start_consuming.assert_called_once()

def test_base_rabbit_consumer_on_message():
    consumer = DummyConsumer(lambda: MagicMock())
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 1
    
    consumer._on_message(mock_channel, mock_method, None, b"body")
    
    assert len(consumer.handled) == 1
    assert consumer.handled[0] == {"deserialized": "body"}
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)

def test_base_rabbit_consumer_on_message_exception():
    consumer = DummyConsumer(lambda: MagicMock())
    # Make _handle raise an exception
    consumer._handle = MagicMock(side_effect=Exception("Failed"))
    
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 1
    
    with pytest.raises(Exception):
        consumer._on_message(mock_channel, mock_method, None, b"body")
