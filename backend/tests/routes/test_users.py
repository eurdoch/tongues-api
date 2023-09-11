import pytest
from httpx import AsyncClient
from bson import ObjectId
from app.models.user import User
from app.auth import Auther

def generate_invalid_token(token):
    return token[:-1] + "0" if token[-1] != "0" else "1"

@pytest.mark.asyncio
async def test_user_get_success(client: AsyncClient, fake_user: User, access_token: str) -> None:
    response = await client.get(
        "/api/v0/users/" + str(fake_user.id),
        headers={
            "Authorization": "Bearer " + access_token
        }
    )
    assert response.status_code == 200
    # TODO add assertions on class data

@pytest.mark.asyncio
async def test_get_nonexistent_user(client: AsyncClient, access_token: str) -> None:
    random_id = str(ObjectId())
    response = await client.get(
        "/api/v0/users/" + random_id,
        headers={
            "Authorization": "Bearer " + access_token
        }
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v0/users",
        json={
            "email": "test_email",
            "password": "test_password",
            "firstName": "test_firstName",
            "lastName": "test_lastName",
            "nativeLanguage": "en-US",
	    "studyLang": "nl-NL",
        } 
    )
    assert response.status_code == 200
    inserted_user = response.json()
    db_user = await User.find_one(User.email == "test_email")
    assert inserted_user['_id'] == str(db_user.id)
    assert inserted_user['email'] == db_user.email
    assert inserted_user['firstName'] == db_user.firstName
    assert inserted_user['lastName'] == db_user.lastName
    assert inserted_user['nativeLanguage'] == db_user.nativeLanguage
    assert inserted_user['studyLang'] == db_user.studyLang

@pytest.mark.asyncio
async def test_get_user_unauthorized(client: AsyncClient, fake_user: User, access_token: str):
    invalid_token = generate_invalid_token(access_token)
    response = await client.get(
        "/api/v0/users/" + str(fake_user.id),
        headers={
            "Authorization": "Bearer " + invalid_token
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_user_already_exists(client: AsyncClient, fake_user: User):
    response = await client.post(
        "/api/v0/users",
        json={
            "email": fake_user.email,
            "password": "",
            "firstName": "",
            "lastName": "",
            "nativeLanguage": "",
	    "studyLang": "",
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_success(client: AsyncClient):
    auther = Auther()
    new_user = User(
        email="william_walker@nicaragua.net",
        password=auther.get_hashed_password("password"),
        firstName="",
        lastName="",
        subscribed=True,
        jwt_secret_key="",
        nativeLanguage="",
        studyLang="",
    )
    inserted_user = await new_user.create()
    response = await client.post(
        "/api/v0/auth",
        json={
            "email": inserted_user.email,
            "password": "password"
        }
    )
    assert response.status_code == 200
    token = response.json()['access_token']
    response = await client.delete(
        "/api/v0/users/" + str(inserted_user.id),
        headers={
            "Authorization": "Bearer " + token
        }
    )
    deleted_user = await User.find_one(User.email == new_user.email)
    assert deleted_user == None

@pytest.mark.asyncio
async def test_delete_unauthorized(client: AsyncClient, fake_user: User, access_token: str):
    invalid_token = generate_invalid_token(access_token)
    response = await client.delete(
        "/api/v0/users/" + str(fake_user.id),
        headers={
            "Authorization": "Bearer " + invalid_token
        }
    )
    assert response.status_code == 401
