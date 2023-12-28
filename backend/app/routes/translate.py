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
from app.utils.language import ISO_TO_LANG, LANG_TO_ISO, ISO_TO_VOICE_ID

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
        "translation": response
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
    parsedStudyLang = studyLang.replace('-', '_')
    parsedNativeLang = nativeLang.replace('-', '_')
    db_word = await Word.find_one(
       Word.word == word,
       Word.language == parsedStudyLang,
    )
    if db_word is None or parsedNativeLang not in db_word.translations:
        translations = translate_word(
            source_language=ISO_TO_LANG[parsedStudyLang],
            target_language=ISO_TO_LANG[parsedNativeLang],
            word=word,
        )
        if db_word is None:
            translations_dict = {}
            translations_dict[parsedNativeLang] = translations
            # generate audio of word
            stream = generate_audio_stream(
                voice_id=ISO_TO_VOICE_ID[parsedStudyLang],
                text=word,
            )
            f = BytesIO()
            with closing(stream) as stream:
                try:
                    f.write(stream.read())
                except IOError as error:
                    print(error)
            f.seek(0)
            content = f.read()
            audio_id = await app.audio_bucket.upload_from_stream("test_file", content, metadata={"contentType": "audio/mp3"})
            new_word = Word(
                word=word,
                language=parsedStudyLang,
                translations=translations_dict,
                audio_id=audio_id,
            )
            await new_word.save()
            return_word = await Word.find_one(Word.word == new_word.word)
            return_word = return_word.__dict__
            return_word['translations'] = return_word['translations'][parsedNativeLang]
            return_word['audio_id'] = str(return_word['audio_id'])
            return return_word
        else:
            db_word.translations[parsedNativeLang] = translations
            await db_word.save()
            return_word = await Word.find_one(Word.word == db_word.word)
            return_word = return_word.__dict__
            return_word['translations'] = return_word['translations'][parsedNativeLang]
            return_word['audio_id'] = str(return_word['audio_id'])
            return return_word
    else:
        return_word = await Word.find_one(Word.word == db_word.word)
        return_word = return_word.__dict__
        return_word['translations'] = return_word['translations'][parsedNativeLang]
        return_word['audio_id'] = str(return_word['audio_id'])
        return return_word

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
