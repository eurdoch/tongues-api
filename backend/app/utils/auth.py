from app.auth import Auther
from app.models.user import User
from fastapi import HTTPException, Header
from typing import Annotated

async def is_authorized(authorization: Annotated[str, Header()]):
    auther = Auther()
    user_id = auther.get_user_from_jwt(authorization)
    user: User = await User.get(user_id)
    if user is None:
        raise HTTPException(401)
    authorized = auther.authorize_user(
        authorization,
        user.jwt_secret_key
    )
    if not authorized:
        raise HTTPException(401)
