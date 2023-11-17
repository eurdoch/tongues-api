from fastapi import (
    APIRouter, 
    Depends,
)
from fastapi.responses import Response
from typing import List
from pydantic import BaseModel
from io import BytesIO
from contextlib import closing
from app.utils.generate import generate_audio_stream
from app.utils.auth import is_authorized
from app.utils.language import ISO_TO_VOICE_ID

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

class GenerateInfo(BaseModel):
    topic: str
    words: List[str]

class Speech(BaseModel):
    text: str
    language: str

@router.post("/speech")
async def generate_speech(speech: Speech): 
    stream = generate_audio_stream(
        ISO_TO_VOICE_ID[speech.language.replace('-','_')], 
        speech.text
    )
    f = BytesIO()
    with closing(stream) as stream:
        try:
            f.write(stream.read())
        except IOError as error:
            print(error)
    f.seek(0)
    content = f.read()
    return Response(content=content, media_type="audio/mp3")
