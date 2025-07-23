from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.blacklist.router import router as blacklist_router
from src.api.reason.router import router as reason_router
from src.core.config import config
from src.core.rabbit.producer import RabbitProducer
from src.utils import logger


rabbit_producer = RabbitProducer(
    url=config.RABBIT_URL, producer_name="blacklist_producer", logger=logger
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with rabbit_producer:
        app.state.rabbit_producer = rabbit_producer
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(blacklist_router, prefix="/blacklist", tags=["Blacklist"])
app.include_router(reason_router, prefix="/reason", tags=["Reason"])
