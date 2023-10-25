from beanie import Document
from pydantic import BaseModel

class UserDAO(Document):
    nativeLanguage: str
    studyLang: str
    firebase_user_id: str

class UserPatch(BaseModel):
    nativeLang: str
    studyLang: str

class User(Document):
    email: str
    nativeLanguage: str
    studyLang: str
    firebase_user_id: str
    stripe_session_id: str = ""
    customer: str = ""
    subscription: str = ""

class NativeLanguage(BaseModel):
    nativeLanguage: str

class SignupForm(BaseModel):
    email: str
    firebase_user_id: str
    nativeLanguage: str
    studyLang: str
