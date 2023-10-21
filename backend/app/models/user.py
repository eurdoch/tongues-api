from beanie import Document
from pydantic import BaseModel

class UserDAO(Document):
    nativeLanguage: str
    studyLang: str
    firebase_user_id: str

class User(Document):
    nativeLanguage: str
    studyLang: str
    firebase_user_id: str

class NativeLanguage(BaseModel):
    nativeLanguage: str

class SignupForm(BaseModel):
    firebase_user_id: str
    nativeLanguage: str
    studyLang: str
