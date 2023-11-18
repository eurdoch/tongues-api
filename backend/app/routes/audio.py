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

# TODO shoudl require admin privs
@router.post("/audio")
async def save_audio(
    file: Annotated[bytes, File()],
):
    # TODO change test_file name to be something more relevant, like section + random_num
    file_id = await app.audio_bucket.upload_from_stream("test_file", file, metadata={"contentType": "audio/mp3"})
    return { 'file_id': str(file_id) }

@router.get("/audio/{id}")
async def get_audio_by_id(
    id: str,
):
    f = BytesIO()
    await app.audio_bucket.download_to_stream(ObjectId(id), f) 
    f.seek(0)
    contents = f.read()
    return Response(content=contents, media_type="audio/webm")

# TODO require admin key
@router.delete("/audio/{id}")
async def delete_audio_by_id(
    id: str,
):
    await app.audio_bucket.delete(ObjectId(id))
