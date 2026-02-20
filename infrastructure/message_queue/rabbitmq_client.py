"""
RabbitMQ client for advanced messaging patterns
"""

import json
from typing import Callable, Optional

import aio_pika

from app.config import settings


class RabbitMQClient:
    """Async RabbitMQ client"""
    
    def __init__(self):
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
    
    async def connect(self):
        """Connect to RabbitMQ"""
        self.connection = await aio_pika.connect_robust(
            settings.CELERY_BROKER_URL,
        )
        self.channel = await self.connection.channel()
    
    async def disconnect(self):
        """Close connection"""
        if self.connection:
            await self.connection.close()
    
    async def declare_queue(self, queue_name: str, durable: bool = True):
        """Declare a queue"""
        await self.channel.declare_queue(queue_name, durable=durable)
    
    async def publish(
        self,
        routing_key: str,
        message: dict,
        exchange: str = "",
    ):
        """Publish message to queue"""
        if not self.channel:
            await self.connect()
        
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
    
    async def consume(
        self,
        queue_name: str,
        callback: Callable,
        prefetch_count: int = 1,
    ):
        """Consume messages from queue"""
        if not self.channel:
            await self.connect()
        
        await self.channel.set_qos(prefetch_count=prefetch_count)
        queue = await self.channel.declare_queue(queue_name, durable=True)
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        body = json.loads(message.body.decode())
                        await callback(body)
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        # Could reject and requeue here
