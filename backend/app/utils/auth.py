from fastapi import Header
from typing import Annotated
from firebase_admin import auth

async def is_authorized(authorization: Annotated[str, Header()]):
    token = authorization.split(' ')[1]
    decoded_token = auth.verify_id_token(token)
