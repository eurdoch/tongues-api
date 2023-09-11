import pytest
from httpx import AsyncClient
from app.models.example import Example
from app.app import app
from bson import ObjectId
import io

def generate_invalid_token(token):
    return token[:-1] + "0" if token[-1] != "0" else "1"

@pytest.fixture
async def fake_audio_id(): 
    file_id: ObjectId = await app.audio_bucket.upload_from_stream(
        "test_file", b"fakedata", metadata={"contentType": "audio/mp3"}
    )
    yield file_id

@pytest.mark.asyncio
async def test_example_create_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v0/examples",
        json={
            "section": "section",
            "language": "language",
            "conversation": [
                {
                    "sentence": "sentence",
                    "audio_id": "64af98b7f2845eb3715d76a2"
                }
            ]
        }
    )
    assert response.status_code == 200
    inserted_example = response.json()
    db_example: Example = await Example.get(inserted_example['_id'])
    assert db_example is not None
    assert db_example.section == "section"
    assert db_example.language == "language"
    assert db_example.conversation[0].sentence == "sentence"
    assert str(db_example.conversation[0].audio_id) == "64af98b7f2845eb3715d76a2"

@pytest.mark.asyncio
async def test_get_example_by_id_success(client: AsyncClient, fake_example: Example, access_token: str):
    response = await client.get(
        "/api/v0/examples/" + str(fake_example.id),
        headers={
            "Authorization": "Bearer " + access_token
        }
    )
    assert response.status_code == 200
    example = response.json()
    assert example['section'] == fake_example.section
    assert example['conversation'][0]['sentence'] == fake_example.conversation[0].sentence
    assert example['language'] == fake_example.language
    assert example['conversation'][0]['audio_id'] == str(fake_example.conversation[0].audio_id)

@pytest.mark.asyncio
async def test_get_example_by_id_unauthorized(client: AsyncClient, fake_example: Example, access_token: str) -> None:
    response = await client.get(
        "/api/v0/examples/" + str(fake_example.id),
        headers={
            "Authorization": "Bearer INVALIDTOKEN"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_examples_by_section_success(client: AsyncClient, fake_example: Example, access_token: str):
    response = await client.get(
        "/api/v0/examples/" + str(fake_example.language) + "/" + str(fake_example.section),
        headers={
            "Authorization": "Bearer " + access_token
        }
    )
    assert response.status_code == 200
    examples = response.json()
    for example in examples:
        assert example['section'] == str(fake_example.section)
        assert example['language'] == str(fake_example.language)

@pytest.mark.asyncio
async def test_get_examples_by_section_unauthorized(client: AsyncClient, access_token: str):
    response = await client.get(
        "/api/v0/examples/language/section",
        headers={
            "Authorization": "Bearer " + generate_invalid_token(access_token)
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_example_ids_by_section_success(client: AsyncClient, access_token: str, fake_example: Example) -> None:
    response = await client.get(
        "/api/v0/examples/" + fake_example.language + "/" + fake_example.section + "/ids",
        headers={
            "Authorization": "Bearer " + access_token
        }
    )
    assert response.status_code == 200
    print(response.json())
    example_ids = response.json()
    assert example_ids[0] == str(fake_example.id)

@pytest.mark.asyncio
async def test_post_file(client: AsyncClient):
    response = await client.post(
        "/api/v0/audio",
        files={ 'file': b'af3fda3ad3edadf' }
    )
    assert response.status_code == 200
    file_id = response.json()['file_id']
    f = io.BytesIO()
    await app.audio_bucket.download_to_stream(ObjectId(file_id), f)
    f.seek(0)
    contents = f.read()
    assert contents == b'af3fda3ad3edadf'

@pytest.mark.asyncio
async def test_get_file(client: AsyncClient, fake_audio_id: ObjectId, access_token: str) -> None:
    response = await client.get(
        "/api/v0/audio/" + str(fake_audio_id),
        headers={
            "Authorization": "Bearer " + access_token
        }
    )
    assert response.status_code == 200
    assert response.content == b"fakedata"