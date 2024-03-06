from fastapi import (
    APIRouter, 
    Body,
    Depends,
    HTTPException,
    Header,
)
from app.utils.auth import is_authorized
from firebase_admin import auth

router = APIRouter(
    prefix="/api/v0",
)

from app.models.user import User
from app.utils.auth import is_authorized

@router.get(
    "/users",
)
async def get_user_by_id(
    authorization: str = Header(),
):
    token = authorization.split(' ')[1]
    decoded_token = auth.verify_id_token(token)
    user: User = await User.find_one(User.firebase_user_id == decoded_token['uid'])
    if user is None:
        raise HTTPException(404)
    return user

@router.put(
     "/users",
)
async def update_user(
     authorization: str = Header(),
     updatedUser: User = Body(),
):
    token = authorization.split(' ')[1]
    decoded_token = auth.verify_id_token(token)
    user: User = await User.find_one(User.firebase_user_id == decoded_token['uid'])
    if user is None or updatedUser.firebase_user_id != user.firebase_user_id:
        raise HTTPException(401)
    user.nativeLanguage = updatedUser.nativeLanguage
    user.studyLanguage = updatedUser.studyLanguage
    await user.save()
    return user

@router.post("/users")
async def add_user(
    user: User = Body(),
):
    existing_user = await User.find_one(User.firebase_user_id == user.firebase_user_id)
    if existing_user is not None:
        raise HTTPException(401)
    new_user = User(
        firebase_user_id=user.firebase_user_id,
        nativeLanguage=user.nativeLanguage,
        studyLanguage=user.studyLanguage,
        messageCount=0,
    )
    inserted_user = await new_user.insert()
    return inserted_user

