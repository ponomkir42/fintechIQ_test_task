import asyncio
import json
from datetime import date

import aio_pika
from asyncpg.exceptions import ForeignKeyViolationError
from sqlalchemy.exc import IntegrityError

from src.core.config import config
from src.core.database.connector import AsyncSessionLocal
from src.core.rabbit.consumer import RabbitConsumer
from src.models import Blacklist
from src.utils import logger


class BlacklistConsumer(RabbitConsumer):
    async def process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            data = json.loads(message.body.decode())
            data["birth_date"] = date.fromisoformat(data["birth_date"])
            self.logger.info(f"[{self.consumer_name}] Consuming message: {data}")
            try:
                async with AsyncSessionLocal() as session:
                    blacklist = Blacklist(**data)
                    session.add(blacklist)
                    await session.commit()
                    self.logger.info(f"[{self.consumer_name}] Person added to blacklist: {data}")
            except IntegrityError as e:
                if isinstance(e.__cause__.__cause__, ForeignKeyViolationError):
                    self.logger.error(f"Invalid reason reference {data}")
                self.logger.error(f"Duplicate blacklist entry {data}")


if __name__ == "__main__":
    consumer = BlacklistConsumer(
        consumer_name="blacklist_consumer",
        queue_name=config.RABBIT_QUEUE,
        rabbit_url=config.RABBIT_URL,
        logger=logger,
    )
    asyncio.run(consumer.run())
