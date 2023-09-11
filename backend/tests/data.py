from app.models.user import User
from app.models.example import Example
from app.auth import Auther
from beanie import PydanticObjectId
from bson import ObjectId

async def add_empty_user() -> User:
    """Adds test users to user collection"""
    auther = Auther()
    empty_user = User(
        email="empty@test.io",
        password=auther.get_hashed_password("password"),
        firstName="firstName",
        lastName="lastName", 
        subscribed=True,
        jwt_secret_key="jwt_secret_key",
        nativeLanguage="en-US",
	studyLang="nl-NL",
    )
    return await empty_user.create()

async def add_empty_example() -> Example:
    fake_example = Example(
        section="section",
        language="language",
        conversation=[
            {
                "sentence": "Hello how are you?",
                "audio_id": PydanticObjectId()
            }
        ]
    ) 
    return await fake_example.create() 
    
