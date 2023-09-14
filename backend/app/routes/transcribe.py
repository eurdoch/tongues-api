from fastapi import (
    APIRouter,
    File,
    Header,
    HTTPException,
    Depends,
    Form,
    UploadFile,
)
from typing import Annotated
import os
import requests

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
    file: Annotated[UploadFile, File()],
    language: Annotated[str, Form()],
    model: Annotated[str, Form()],
):
    files = {
        'file': ('speech.webm', file.file),
    }
    data = {
        'model': model,
        'language': language,
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
    print(r.status_code)
    print(r.json())
    transcription = r.json()['text']
    transcription = transcription.strip()
    return {
        "text": transcription,
    }
