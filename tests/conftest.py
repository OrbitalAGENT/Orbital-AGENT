# tests/conftest.py
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="session", autouse=True)
def mock_external_dependencies():
    """Global mocks for external services"""
    with patch('redis.StrictRedis') as mock_redis, \
         patch('requests.Session') as mock_requests, \
         patch('kafka.KafkaProducer') as mock_kafka:
        
        # Configure mock returns
        mock_redis.return_value.ping.return_value = True
        mock_requests.return_value.get.return_value.status_code = 200
        mock_kafka.return_value.send.return_value.get.return_value = True
        
        yield
