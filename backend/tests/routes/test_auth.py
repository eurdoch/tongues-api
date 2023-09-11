import pytest
from httpx import AsyncClient
from tests.data import add_empty_user

@pytest.mark.asyncio
async def test_successful_login(client: AsyncClient) -> None:
    inserted_user = await add_empty_user()
    response = await client.post(
        "/api/v0/auth",
        json={
            "email": inserted_user.email,
            "password": "password",
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result['token_type'] == "bearer"
    # TODO parse token and check against id

@pytest.mark.asyncio
async def test_wrong_password_login(client: AsyncClient) -> None:
    inserted_user = await add_empty_user()
    response = await client.post(
        "/api/v0/auth",
        json={
            "email": inserted_user.email,
            "password": "weekekresh"
        }
    )
    assert response.status_code == 401

async def test_non_existent_user_login(client: AsyncClient) -> None:
    await add_empty_user()
    response = await client.post(
        "/api/v0/auth",
        json={
            "email": "jabbajoo",
            "password": "password"
        }
    )
    assert response.status_code == 401