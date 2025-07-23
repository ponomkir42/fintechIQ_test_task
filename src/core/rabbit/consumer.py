import asyncio
from abc import ABC, abstractmethod
from logging import Logger

import aio_pika


class RabbitConsumer(ABC):
    def __init__(
        self,
        consumer_name: str,
        queue_name: str,
        rabbit_url: str,
        logger: Logger,
        prefetch_count: int = 100,
    ):
        self.consumer_name = consumer_name
        self.logger = logger
        self.queue_name = queue_name
        self.rabbit_url = rabbit_url
        self.prefetch_count = prefetch_count
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.abc.AbstractChannel | None = None

    @abstractmethod
    async def process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        pass

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.rabbit_url)
        self.logger.info(f"[{self.consumer_name}] Connected to RabbitMQ server")
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=self.prefetch_count)

        queue = await self.channel.declare_queue(self.queue_name, durable=True)
        await queue.consume(self.process_message)

        await asyncio.Future()

    async def run(self) -> None:
        if self.connection:
            async with self.connection:
                await self.connect()
        else:
            await self.connect()
