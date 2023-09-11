from app.models.example import Example
from app.models.user import User
from app.auth import Auther
from app.app import app
from typing import Annotated
from pydantic import BaseModel
from beanie import PydanticObjectId

from io import BytesIO
from bson import ObjectId

from fastapi import (
    APIRouter, 
    HTTPException,
    Header,
    File,
    Response,
    Query,
    Depends,
)

from app.utils.auth import is_authorized

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

class IdProjector(BaseModel):
    id: PydanticObjectId

    class Settings:
        projection = {"_id": 1}

# TODO require admin priveleges!
@router.post("/examples")
async def save_example(example: Example):
    inserted_example = await Example.insert_one(example)
    return inserted_example

"""
    Returns list of all example ids by section and language
"""
@router.get("/examples")
async def get_ids_for_section(
    section: str = Query(), 
    language: str = Query(),
    authorization = Header(),
):
    examples = await Example.find(
        Example.section == section, 
        Example.language == language
    ).to_list()
    example_ids = []
    for example in examples:
        example_ids.append(str(example.id))
    return example_ids

@router.get("/examples/{id}")
async def get_example_by_id(
    id: str, 
):
    example: Example = await Example.get(id)
    return example

# Require additional admin priveleges
@router.delete("/examples/{id}")
async def delete_example_by_id(
    id: str,
):
    example: Example = await Example.get(id)
    for sentence in example.conversation:
        app.audio_bucket.delete(ObjectId(sentence.audio_id))
    await example.delete()

@router.get("/sections")
async def get_distinct_sections(
    authorization = Header(),
):
    return await app.db.Example.distinct('section')

# TODO require admin priveleges
@router.post("/audio")
async def save_example_audio(
    file: Annotated[bytes, File()],
):
    # TODO change test_file name to be something more relevant, like section + random_num
    file_id = await app.audio_bucket.upload_from_stream("test_file", file, metadata={"contentType": "audio/mp3"})
    return { 'file_id': str(file_id) }

@router.get("/audio/{id}")
async def get_audio_by_id(
    id: str,
    authorization = Header(),
):
    f = BytesIO()
    await app.audio_bucket.download_to_stream(ObjectId(id), f) 
    f.seek(0)
    contents = f.read()
    return Response(content=contents, media_type="audio/mp3")

# TODO require admin key
@router.delete("/audio/{id}")
async def delete_audio_by_id(
    id: str,
):
    await app.audio_bucket.delete(ObjectId(id))
