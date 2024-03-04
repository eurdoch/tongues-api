from contextlib import closing
from io import BytesIO
import json
 
from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from app.models.translate import (
    TranslationRequest, 
    Word,
)
from app.app import app
from app.utils.auth import is_authorized
from app.utils.generate import generate_audio_stream
from app.utils.translate import translate, translate_word
from app.utils.models import get_chat_response

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

@router.post(
    "/translate"
)
async def translate_text(
    translationRequest: TranslationRequest,
):
    response = translate(
        source_language=translationRequest.sourceLang,
        target_language=translationRequest.targetLang,
        sentence=translationRequest.sentence
    )
    return {
        "text": response
    }

def reverse_dict(original_dict):
    switched_dict = {value: key for key, value in original_dict.items()}
    return switched_dict

@router.get(
    "/word"
)
async def get_word(
    word: str = Query(),
    nativeLang: str = Query(),
    studyLang: str = Query(),
):
	translation = translate_word(studyLang, nativeLang, word)	
	return { "text": translation }

@router.get(
    "/explanation"
)
async def get_explanation(
    text: str = Query(),
    nativeLang: str = Query(),
    studyLang: str = Query(),
):
    response = get_chat_response(f"Explain the {studyLang} text {text} using {nativeLang}.")
    return { "text": response }

@router.get("/analysis")
async def get_analysis(
    word: str = Query(),
    nativeLang: str = Query(),
    studyLang: str = Query(),
):
    response = get_chat_response(f"Give a brief explanation using the {nativeLang} language of the {studyLang} word '{word}'")
    return { "text": response }

@router.get(
    "/conjugations"
)
async def get_conjugations(
    word: str = Query(),
    language: str = Query(),
):
    # TODO starting with just call to Claude
    response = get_chat_response(f"Generate all tenses and conjugations of the {language} verb '{word}', including the infinitive and participle cases.  ONLY return a JSON object.")
    return json.loads(response.replace('\n', ''))
