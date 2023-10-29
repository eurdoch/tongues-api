from app.auth import Auther
from fastapi import HTTPException, Header
from typing import Annotated
from pydantic import BaseModel
from firebase_admin import auth
from app.models.user import User

class UserSubscriptionStatus(BaseModel):
    subscription: str

async def is_authorized(authorization: Annotated[str, Header()]):
    token = authorization.split(' ')[1]
    decoded_token = auth.verify_id_token(token)
    user = await User.find_one(User.firebase_user_id == decoded_token['uid']).project(UserSubscriptionStatus)
    if user.subscription != 'active' and user.subscription != 'trial':
        raise HTTPException(401)
