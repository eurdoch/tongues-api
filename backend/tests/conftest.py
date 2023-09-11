from typing import Iterator

import pytest
from asgi_lifespan import LifespanManager
from decouple import config
from fastapi import FastAPI
from httpx import AsyncClient

from app.config import CONFIG
from app.models.user import User
from app.models.example import Example
from tests.data import add_empty_user
from tests.data import add_empty_example

CONFIG.testing = True
CONFIG.mongo_uri = config("TEST_MONGO_URI", default="mongodb://localhost:27017")

from app.main import app

async def clear_database(server: FastAPI) -> None:
    for collection in await server.db.list_collections():
        await server.db[collection["name"]].delete_many({})
    
@pytest.fixture
async def client() -> Iterator[AsyncClient]:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as _client:
            try:
                yield _client
            except Exception as exc:
                print(exc)
            finally:
                await clear_database(app)

@pytest.fixture
async def fake_user() -> User:
    inserted_user = await add_empty_user()
    yield inserted_user

@pytest.fixture
async def fake_example() -> Example:
    yield await add_empty_example()

@pytest.fixture
async def access_token(client: AsyncClient, fake_user: User) -> str:
    # TODO this is bad form, should not use code that is being tested, what if it breaks!
    response = await client.post(
        "/api/v0/auth",
        json={
            "email": fake_user.email,
            "password": "password"
        }
    )
    assert response.status_code == 200
    yield response.json()['access_token']