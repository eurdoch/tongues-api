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

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

class GenerateInfo(BaseModel):
    topic: str
    words: List[str]

class Speech(BaseModel):
    sentence: str
    voice_id: str

@router.post("/generatespeech")
async def generate_speech(speech: Speech): 
    stream = generate_audio_stream(speech.voice_id, speech.sentence)
    f = BytesIO()
    with closing(stream) as stream:
        try:
            f.write(stream.read())
        except IOError as error:
            print(error)
    f.seek(0)
    content = f.read()
    return Response(content=content, media_type="audio/mp3")
