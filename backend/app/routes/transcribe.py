from fastapi import (
    APIRouter,
    File,
    Header,
    HTTPException,
    Depends,
)
from typing import Annotated
import os
import requests
from io import BytesIO

from app.utils.auth import is_authorized

from dotenv import load_dotenv
load_dotenv()

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

@router.post(
    "/transcription"
)
async def get_audio_transcription(
    file: Annotated[bytes, File()],
):
    f = BytesIO(file)
    files = {
        'file': ('speech.webm', f),
    }
    data = {
        'model': 'whisper-1'
    }
    headers = {
        "Authorization": "Bearer " + os.getenv('OPENAI_API_KEY')
    }
    r = requests.post(
        url='https://api.openai.com/v1/audio/transcriptions',
        files=files,
        data=data,
        headers=headers
    )
    transcription = r.json()['text']
    transcription = transcription.strip()
    return {
        "text": transcription,
    }
