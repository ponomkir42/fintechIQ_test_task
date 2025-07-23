import pytest
from faker import Faker

fake = Faker(locale="ru_RU")
BASE_URL = "/reason"


@pytest.mark.asyncio
async def test_get_all(client, reason_db):
    response = await client.get(BASE_URL)
    assert response.status_code == 200
    assert response.json()["meta"]["found"] != 0


@pytest.mark.asyncio
async def test_get_by_id(client, reason_db):
    response = await client.get(f"{BASE_URL}/{str(reason_db.id)}/")
    assert response.status_code == 200
    assert response.json()["id"] == reason_db.id


@pytest.mark.asyncio
async def test_create(client):
    payload = {"name": fake.word(), "slug": fake.word(), "description": fake.catch_phrase()}

    response = await client.post(BASE_URL, json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == payload["name"]
    assert response.json()["slug"] == payload["slug"]
    assert response.json()["description"] == payload["description"]


@pytest.mark.asyncio
async def test_update(client, reason_db):
    update_data = {"name": fake.word(), "slug": fake.word(), "description": fake.catch_phrase()}
    response = await client.patch(f"{BASE_URL}/{str(reason_db.id)}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["slug"] == update_data["slug"]
    assert response.json()["description"] == update_data["description"]


@pytest.mark.asyncio
async def test_delete(client, reason_db):
    response = await client.delete(f"{BASE_URL}/{str(reason_db.id)}/")
    assert response.status_code == 204

    response = await client.get(f"{BASE_URL}/{str(reason_db.id)}/")
    assert response.status_code == 404
