from pydantic import BaseModel
from typing import Dict, List
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
    translations: Dict[str, List[str]]
