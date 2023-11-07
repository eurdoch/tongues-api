from fastapi import (
    APIRouter, 
    Body,
    Depends,
    HTTPException,
    Header,
)
from secrets import token_urlsafe
import json
from app.auth import Auther
from app.utils.auth import is_authorized
from firebase_admin import auth

router = APIRouter(
    prefix="/api/v0",
)

# TODO This is messy, all authorization should be handled with a single class/function
from app.core.auther import get_auther
from app.auth import Auther
from app.models.user import User, SignupForm, UserDAO
from app.utils.auth import is_authorized

auther = Auther()

import os

@router.get(
    "/verify",
    dependencies=[Depends(is_authorized)],
)
async def verify_token():
    pass

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
    return UserDAO.parse_obj(user)

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
    signup_form: SignupForm = Body(),
):
    existing_user = await User.find_one(User.firebase_user_id == signup_form.firebase_user_id)
    if existing_user is not None:
        raise HTTPException(401)
    new_user = User(
        firebase_user_id=signup_form.firebase_user_id,
        nativeLanguage=signup_form.nativeLanguage,
        studyLanguage=signup_form.studyLanguage,
    )
    inserted_user = await new_user.insert()
    return UserDAO.parse_obj(inserted_user)

# TODO update this, needs to be delete function for user
# @router.delete(
#     "/users",
#     dependencies=[Depends(is_authorized)],
# )
# async def delete_user_by_id(
#     authorization: str = Header(),
# ):
#     user_id = auther.get_user_from_jwt(authorization)
#     user: User = await User.get(user_id)
#     if user is None:
#         raise HTTPException(401)
#     result = await user.delete()
#     return True
