# tests/integration/test_event_bus.py
import pytest
import asyncio
from src.event_bus import EventBus

@pytest.fixture
def event_bus():
    return EventBus(config={
        "protocol": "memory",
        "bootstrap_servers": ["localhost:9092"]
    })

@pytest.mark.asyncio
async def test_pubsub_workflow(event_bus):
    received_messages = []
    
    async def message_handler(payload):
        received_messages.append(payload)
    
    await event_bus.initialize()
    await event_bus.subscribe("test_topic", message_handler)
    await event_bus.publish("test_topic", {"test": "data"})
    
    await asyncio.sleep(0.1)
    assert len(received_messages) == 1
    assert received_messages[0]["test"] == "data"
