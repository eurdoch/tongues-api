from pydantic import BaseModel
from typing import Dict
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

class Word(Document):
    audio_id: PydanticObjectId
    word: str
    language: str
    explanation: Dict[str, str]

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
