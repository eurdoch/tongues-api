from beanie import Document
from pydantic import BaseModel

# class BillingAddress(BaseModel):
#     address: str
#     city: str
#     state: str
#     zipCode: str
 
# class PaymentOption(BaseModel):
#     _id: str
#     creditCard: str
#     exp: str
#     cvc: str
#     billingAddress: BillingAddress
#     primary: bool

class UserDAO(Document):
    revcat_id: str
    nativeLanguage: str
    studyLang: str
    firebase_user_id: str

# class User(Document):
#     firstName: str
#     lastName: str
#     password: str
#     email: str
#     jwt_secret_key: str
#     subscribed: bool
#     nativeLanguage: str
#     studyLang: str
class User(Document):
    revcat_id: str
    nativeLanguage: str
    studyLang: str
    firebase_user_id: str

class NativeLanguage(BaseModel):
    nativeLanguage: str

# class SignupForm(BaseModel):
#     email: str
#     password: str
#     firstName: str
#     lastName: str
#     nativeLanguage: str
#     studyLang: str

class SignupForm(BaseModel):
    firebase_user_id: str
    revcat_id: str
    nativeLanguage: str
    studyLang: str
