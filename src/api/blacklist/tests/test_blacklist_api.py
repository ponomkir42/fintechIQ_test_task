import pytest
from faker import Faker

fake = Faker(locale="ru_RU")
BASE_URL = "/blacklist"


@pytest.mark.asyncio
async def test_get_empty_list(client):
    response = await client.get(BASE_URL)
    assert response.status_code == 200
    assert response.json()["meta"]["found"] == 0
    assert response.json()["items"] == []


@pytest.mark.asyncio
async def test_create_blacklist_one_person(client, reason_db):
    payload = [
        {
            "first_name": fake.first_name_male(),
            "last_name": fake.last_name_male(),
            "middle_name": None,
            "birth_date": fake.date(),
            "reason_id": reason_db.id,
        },
    ]
    response = await client.post(BASE_URL, json=payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_list(client):
    response = await client.get(BASE_URL)
    assert response.status_code == 200
    assert response.json()["meta"]["found"] == 1
    assert len(response.json()["items"]) == 1


@pytest.mark.asyncio
async def test_create_blacklist_multiple_persons(client, reason_db):
    payload = [
        {
            "first_name": fake.first_name_male(),
            "last_name": fake.last_name_male(),
            "middle_name": None,
            "birth_date": fake.date(),
            "reason_id": reason_db.id,
        },
        {
            "first_name": fake.first_name_male(),
            "last_name": fake.last_name_male(),
            "middle_name": fake.middle_name_male(),
            "birth_date": fake.date(),
            "reason_id": reason_db.id,
        },
    ]
    response = await client.post(BASE_URL, json=payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_blacklist_wrong_name_format(client):
    payload = [
        {
            "first_name": "John",
            "last_name": "Dow",
            "middle_name": None,
            "birth_date": fake.date(),
            "reason_id": 1,
        }
    ]
    response = await client.post(BASE_URL, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_blacklist_wrong_reason_reference(client):
    payload = [
        {
            "first_name": fake.first_name_male(),
            "last_name": fake.last_name_male(),
            "middle_name": None,
            "birth_date": fake.date(),
            "reason_id": "42",
        }
    ]
    response = await client.post(BASE_URL, json=payload)
    assert response.status_code == 207
    assert response.json()["errors"][0]["error"] == "Invalid reason reference"


@pytest.mark.asyncio
async def test_get_one(client, blacklist_db):
    response = await client.get(f"{BASE_URL}/{str(blacklist_db.id)}/")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(blacklist_db.id)


@pytest.mark.asyncio
async def test_search(client, blacklist_db):
    params = {
        "first_name": blacklist_db.first_name,
        "last_name": blacklist_db.last_name,
        "middle_name": blacklist_db.middle_name,
    }
    response = await client.get(f"{BASE_URL}/search/", params=params)
    assert response.status_code == 200
    assert response.json()["meta"]["found"] != 0


@pytest.mark.asyncio
async def test_update(client, blacklist_db):
    update_data = {
        "first_name": fake.first_name_male(),
    }
    response = await client.patch(f"{BASE_URL}/{str(blacklist_db.id)}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["first_name"] == update_data["first_name"]


@pytest.mark.asyncio
async def test_queue_blacklist_success(client, reason_db):
    payload = [
        {
            "first_name": fake.first_name_male(),
            "last_name": fake.last_name_male(),
            "middle_name": None,
            "birth_date": fake.date(),
            "reason_id": reason_db.id,
        },
    ]

    response = await client.post(f"{BASE_URL}/queue/", json=payload)
    assert response.status_code == 200

    body = response.json()

    assert len(body["sent"]) == 1

    sent = body["sent"][0]

    assert sent["first_name"] == payload[0]["first_name"]
    assert sent["reason_id"] == reason_db.id


@pytest.mark.asyncio
async def test_queue_blacklist_fail(client, blacklist_db):
    payload = [
        {
            "first_name": blacklist_db.first_name,
            "last_name": blacklist_db.last_name,
            "middle_name": blacklist_db.middle_name,
            "birth_date": str(blacklist_db.birth_date),
            "reason_id": blacklist_db.reason_id,
        }
    ]

    response = await client.post(f"{BASE_URL}/queue/", json=payload)

    assert response.status_code == 207

    body = response.json()

    assert len(body["sent"]) == 0
    assert len(body["errors"]) == 1

    errors = body["errors"][0]

    assert errors["item"]["first_name"] == payload[0]["first_name"]
    assert errors["item"]["reason_id"] == payload[0]["reason_id"]


@pytest.mark.asyncio
async def test_delete(client, blacklist_db):
    response = await client.delete(f"{BASE_URL}/{str(blacklist_db.id)}/")
    assert response.status_code == 204

    response = await client.get(f"{BASE_URL}/{str(blacklist_db.id)}/")
    assert response.status_code == 404
