from secrets import token_urlsafe

from app.models.user import User
from app.models.login import Login
from app.models.token import Token
from app.auth import Auther

from fastapi import (
    APIRouter,
    HTTPException,
    Body
)

router = APIRouter(
    prefix="/api/v0"
)

# # TODO clean this up, refactor into Auther class, do something you lazy fuck
# def is_authorized(authorization: str, user: User): 
#     auther = Auther()
#     return auther.authorize_user(
#         str(user.id),
#         authorization,
#         user.jwt_secret_key
#     )

@router.post(
    "/auth",
    summary="Get access token for login",
    response_model=Token
)
async def login(login: Login = Body()):
    auther = Auther()
    user = await User.find_one(User.email == login.email)
    if user is None:
        raise HTTPException(401)
    authorized = auther.verify_password(login.password, user.password)
    if not authorized:
        raise HTTPException(401)
    jwt_secret_key = token_urlsafe(64)
    await user.set({ User.jwt_secret_key: jwt_secret_key }) 
    access_token = auther.create_jwt(str(user.id), jwt_secret_key)
    return Token(
        access_token=access_token,
        user_id=str(user.id),
        token_type="bearer"
    )