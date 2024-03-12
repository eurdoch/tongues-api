from beanie import Document
from pydantic import BaseModel

class UserDAO(Document):
    nativeLanguage: str
    studyLanguage: str
    firebase_user_id: str

class UserPatch(BaseModel):
    nativeLang: str
    studyLang: str

class User(Document):
    firebase_user_id: str
    studyLanguage: str
    nativeLanguage: str
    messageCount: int
    subscribed: bool = False
    stripeCustomerId: str = ""

class SupportTicket(Document):
    email: str
    message: str
    date: str
    user: User

class NativeLanguage(BaseModel):
    nativeLanguage: str

class SignupForm(BaseModel):
    firebase_user_id: str
    nativeLanguage: str
    studyLanguage: str
