from pydantic import BaseModel
from beanie import Document, PydanticObjectId

class TranslationRequest(BaseModel):
    sentence: str
    sourceLang: str
    targetLang: str

class TranslationResponse(BaseModel):
    translatedText: str
    detectedSourceLanguage: str

class WordInfo(BaseModel):
    word: str
    studyLang: str
    nativeLang: str

class Explanation(BaseModel):
    nl_NL: str = ""
    es_US: str = ""
    en_US: str = ""
    de_DE: str = ""

class Word(Document):
    audio_id: PydanticObjectId
    word: str
    language: str
    explanation: Explanation

class WordShortView(BaseModel):
    audio_id: PydanticObjectId
    word: str
    language: str
    explanation: str

    class Settings:
        projection = {
            "audio_id": 1,
            "word": 1,
            "language": 1,
            # TODO generalize using init argument
            "explanation": "$explanation.es_US",
        }
