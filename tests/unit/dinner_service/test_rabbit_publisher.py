import pytest
from unittest.mock import MagicMock
from app.services.dinner_service.infrastructure.messaging.rabbit_publisher import RabbitDinnerPublisher
from app.services.dinner_service.domain.entities import DinnerTransaction
from datetime import UTC, datetime

pytestmark = pytest.mark.unit

def test_rabbit_dinner_publisher_serialize():
    pub = RabbitDinnerPublisher(connection_factory=lambda: MagicMock())
    dt = datetime(2026, 5, 30, 12, 0, 0, tzinfo=UTC)
    dinner = DinnerTransaction(amount=100.0, card_number="1234", restaurant_id="R1", timestamp=dt)
    
    serialized = pub._serialize(dinner)
    
    assert "100.0" in serialized
    assert "1234" in serialized
    assert "R1" in serialized
    assert dt.isoformat() in serialized

def test_rabbit_dinner_publisher_publish_dinner(monkeypatch):
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_conn.channel.return_value = mock_channel
    
    pub = RabbitDinnerPublisher(connection_factory=lambda: mock_conn)
    dt = datetime(2026, 5, 30, 12, 0, 0, tzinfo=UTC)
    dinner = DinnerTransaction(amount=100.0, card_number="1234", restaurant_id="R1", timestamp=dt)
    
    pub.publish_dinner(dinner)
    mock_channel.basic_publish.assert_called_once()
