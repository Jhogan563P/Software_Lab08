import pytest
from unittest.mock import MagicMock
from app.services.notifications_service.infrastructure.messaging.publisher import RabbitRewardProcessedPublisher

pytestmark = pytest.mark.unit

def test_rabbit_reward_processed_publisher_serialize():
    pub = RabbitRewardProcessedPublisher(connection_factory=lambda: MagicMock())
    payload = {"customer_id": "C1", "points": 10, "cashback": 1.0}
    
    serialized = pub._serialize(payload)
    
    assert "C1" in serialized
    assert "10" in serialized
    assert "1.0" in serialized

def test_rabbit_reward_processed_publisher_publish(monkeypatch):
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_conn.channel.return_value = mock_channel
    
    pub = RabbitRewardProcessedPublisher(connection_factory=lambda: mock_conn)
    payload = {"customer_id": "C1", "points": 10, "cashback": 1.0}
    
    pub.publish(payload)
    mock_channel.basic_publish.assert_called_once()
