from datetime import datetime

import pytest
import pytest_asyncio
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import config
from src.core.database.connector import get_db_session
from src.main import app as fastapi_app
from src.models import Base, Blacklist, Reason

faker = Faker(locale="ru_RU")


class DummyProducer:
    async def send_message(self, queue_name: str, message: dict):
        return


async def async_database_exists(engine) -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
        return True
    except Exception:
        return False


async def async_create_database(engine):
    temp_engine = create_async_engine(
        engine.url.set(database="postgres").render_as_string(hide_password=False)
    )
    async with temp_engine.connect() as conn:
        await conn.execute(text("COMMIT"))
        await conn.execute(text(f'CREATE DATABASE "{engine.url.database}"'))
    await temp_engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_and_drop_tables():
    engine = create_async_engine(config.POSTGRES_TESTS_URL, echo=False, future=True)

    if not await async_database_exists(engine):
        await async_create_database(engine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(config.POSTGRES_TESTS_URL, echo=False, future=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as session:
        yield session
    await engine.dispose()


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    async def _override():
        yield db_session

    fastapi_app.dependency_overrides[get_db_session] = _override
    yield
    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://localhost:8000"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def reason_db(db_session: AsyncSession) -> Reason:
    reason = Reason(
        name=faker.word(),
        slug=faker.word(),
        description=faker.catch_phrase(),
    )
    db_session.add(reason)
    await db_session.commit()
    await db_session.refresh(reason)
    yield reason


@pytest_asyncio.fixture
async def blacklist_db(db_session: AsyncSession) -> Blacklist:
    blacklist = Blacklist(
        first_name=faker.first_name_male(),
        last_name=faker.last_name_male(),
        middle_name=faker.middle_name_male(),
        birth_date=datetime.now().date(),
        reason_id=1,
    )
    db_session.add(blacklist)
    await db_session.commit()
    await db_session.refresh(blacklist)
    yield blacklist


@pytest.fixture(autouse=True)
def override_rabbit_producer():
    fastapi_app.state.rabbit_producer = DummyProducer()
    yield
