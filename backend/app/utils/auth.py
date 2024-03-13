from fastapi import Header, HTTPException
from typing import Annotated
from firebase_admin import auth

async def is_authorized(authorization: Annotated[str, Header()]):
    token = authorization.split(' ')[1]
    decoded_token = auth.verify_id_token(token)
	firebaseUser = auth.get_user(decoded_token['uid']
	if not firebaseUser.email_verified:
		raise HTTPException(401)
