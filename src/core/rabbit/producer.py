import json
from logging import Logger

import aio_pika
from aio_pika import Message, RobustChannel, RobustConnection


class RabbitProducer:
    def __init__(self, url: str, producer_name: str, logger: Logger):
        self.logger = logger
        self.producer_name = producer_name
        self.url = url
        self.connection: RobustConnection | None = None
        self.channel: RobustChannel | None = None

    async def __aenter__(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.logger.info(f"[{self.producer_name}] Connected to RabbitMQ server")
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=100)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.connection.close()

    async def send_message(self, routing_key: str, message_body: str):
        if not self.channel:
            raise RuntimeError("RabbitMQ channel is not initialized")
        message = Message(
            body=json.dumps(message_body).encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.channel.default_exchange.publish(message, routing_key=routing_key)
