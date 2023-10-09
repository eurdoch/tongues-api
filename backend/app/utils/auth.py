from app.auth import Auther
from app.models.user import User
from fastapi import HTTPException, Header
from typing import Annotated
from firebase_admin import auth

async def is_authorized(authorization: Annotated[str, Header()]):
    token = authorization.split(' ')[1]
    decoded_token = auth.verify_id_token(token)
    uid = decoded_token['uid']
    print(uid)
