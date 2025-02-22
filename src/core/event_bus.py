# orbital-agent/src/event_bus/event_bus.py
import logging
import json
import asyncio
from typing import Dict, Callable, Optional, List, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import ssl
from functools import wraps
import time

logger = logging.getLogger(__name__)

class EventBusError(Exception):
    """Base exception for event bus operations"""

@dataclass
class Event:
    topic: str
    payload: bytes
    headers: Dict[str, str]
    timestamp: float = time.time()
    message_id: Optional[str] = None

class BaseConnector(ABC):
    @abstractmethod
    async def connect(self):
        """Establish connection to broker"""
        
    @abstractmethod
    async def disconnect(self):
        """Close connection gracefully"""
        
    @abstractmethod
    async def publish(self, event: Event):
        """Publish event to topic"""
        
    @abstractmethod
    async def subscribe(self, topic: str, callback: Callable[[Event], None]):
        """Subscribe to topic with callback"""

class KafkaConnector(BaseConnector):
    def __init__(self, config: Dict):
        self.config = config
        self._producer = None
        self._consumer = None

    async def connect(self):
        try:
            from kafka import KafkaProducer, KafkaConsumer
            self._producer = KafkaProducer(
                bootstrap_servers=self.config['bootstrap_servers'],
                security_protocol='SSL',
                ssl_cafile=self.config['ssl_cafile'],
                ssl_certfile=self.config['ssl_certfile'],
                ssl_keyfile=self.config['ssl_keyfile'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("Connected to Kafka cluster")
        except Exception as e:
            logger.error(f"Kafka connection failed: {str(e)}")
            raise EventBusError("Kafka connection error")

    async def disconnect(self):
        if self._producer:
            self._producer.close()

    async def publish(self, event: Event):
        future = self._producer.send(
            event.topic,
            value=event.payload,
            headers=[(k, v.encode()) for k,v in event.headers.items()]
        )
        try:
            await future.get(timeout=self.config.get('timeout', 10))
        except Exception as e:
            logger.error(f"Message publish failed: {str(e)}")
            raise EventBusError("Publish error")

    async def subscribe(self, topic: str, callback: Callable[[Event], None]):
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.config['bootstrap_servers'],
            security_protocol='SSL',
            ssl_cafile=self.config['ssl_cafile'],
            ssl_certfile=self.config['ssl_certfile'],
            ssl_keyfile=self.config['ssl_keyfile'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        for msg in consumer:
            event = Event(
                topic=msg.topic,
                payload=msg.value,
                headers=dict(msg.headers),
                message_id=msg.offset
            )
            await callback(event)

class AMQPConnector(BaseConnector):
    def __init__(self, config: Dict):
        self.config = config
        self._connection = None
        self._channel = None

    async def connect(self):
        try:
            import aio_pika
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            self._connection = await aio_pika.connect_robust(
                host=self.config['host'],
                port=self.config['port'],
                login=self.config['user'],
                password=self.config['password'],
                ssl=ssl_context,
                timeout=self.config.get('timeout', 10)
            )
            self._channel = await self._connection.channel()
            logger.info("Connected to AMQP broker")
        except Exception as e:
            logger.error(f"AMQP connection failed: {str(e)}")
            raise EventBusError("AMQP connection error")

    async def disconnect(self):
        if self._connection:
            await self._connection.close()

    async def publish(self, event: Event):
        message = aio_pika.Message(
            body=event.payload,
            headers=event.headers,
            message_id=event.message_id,
            timestamp=event.timestamp
        )
        await self._channel.default_exchange.publish(
            message,
            routing_key=event.topic
        )

    async def subscribe(self, topic: str, callback: Callable[[Event], None]):
        queue = await self._channel.declare_queue(topic, durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                event = Event(
                    topic=message.routing_key,
                    payload=message.body,
                    headers=message.headers,
                    message_id=message.message_id,
                    timestamp=message.timestamp
                )
                try:
                    await callback(event)
                    await message.ack()
                except Exception as e:
                    await message.nack()
                    logger.error(f"Message processing failed: {str(e)}")

class EventBus:
    _instance = None
    
    def __new__(cls, config: Dict):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.config = config
            cls._instance.connector = cls._create_connector(config)
            cls._instance.subscriptions = {}
        return cls._instance

    @staticmethod
    def _create_connector(config: Dict) -> BaseConnector:
        protocol = config.get('protocol', 'kafka')
        if protocol == 'kafka':
            return KafkaConnector(config)
        elif protocol == 'amqp':
            return AMQPConnector(config)
        raise EventBusError(f"Unsupported protocol: {protocol}")

    async def initialize(self):
        """Initialize connection pool"""
        await self.connector.connect()

    async def shutdown(self):
        """Cleanup resources"""
        await self.connector.disconnect()

    async def publish(self, topic: str, payload: Dict, headers: Optional[Dict] = None):
        """Publish message to event bus"""
        event = Event(
            topic=topic,
            payload=json.dumps(payload).encode(),
            headers=headers or {},
            message_id=self._generate_message_id()
        )
        try:
            await self.connector.publish(event)
            logger.debug(f"Published to {topic}: {event.message_id}")
        except Exception as e:
            logger.error(f"Publish failed: {str(e)}")
            raise EventBusError("Message publish failed") from e

    async def subscribe(self, topic: str, callback: Callable[[Dict], None]):
        """Subscribe to topic with message handler"""
        if topic in self.subscriptions:
            logger.warning(f"Already subscribed to {topic}")
            return

        async def wrapped_callback(event: Event):
            try:
                payload =<i class="fl-spin"></i>
