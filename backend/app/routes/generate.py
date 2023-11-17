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

ISO_TO_VOICE_ID = {
    'es_ES': 'Enrique',
    'en_US': 'Joey',
    'nl_NL': 'Ruben',
    'es_US': 'Lupe',
    'de_DE': 'Hans',
    'fr_FR': 'Mathieu',
    'it_IT': 'Giorgio',
    'is_IS': 'Karl',
    'pt_PT': 'Cristiano',
    'pt_BR': 'Ricardo',
    'ru_RU': 'Maxim',
    'ja_JP': 'Takumi',
    'arb': 'Zeina',
    'sv_SE': 'Astrid',
}

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
