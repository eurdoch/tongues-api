from fastapi import (
    APIRouter,
    File,
    Depends,
    Form,
    UploadFile,
)
from typing import Annotated
import os
import requests

from app.utils.auth import is_authorized
from app.utils.chat import is_valid_grammar
from app.utils.chat import explain_invalid_grammar
from app.utils.language import LANG_TO_ISO

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
        'language': LANG_TO_ISO[language][:2],
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
    #if (is_valid_grammar(text=transcription, language=language)):
    return {
        "is_grammar_valid": True, # For now, always return True, until you can figure out how to get grammar working
        "text": transcription.strip(),
    }
    #else:
    #    grammar_explanation = explain_invalid_grammar(text=transcription, language=language)
    #    return {
    #        "is_grammar_valid": False,
    #        "text": grammar_explanation,
    #    }
