from fastapi import (
    APIRouter, 
    Body,
    Depends,
    HTTPException,
    Header,
)
from secrets import token_urlsafe
from app.auth import Auther
from app.models.user import NativeLanguage
from app.utils.auth import is_authorized

router = APIRouter(
    prefix="/api/v0",
)

# TODO This is messy, all authorization should be handled with a single class/function
from app.core.auther import get_auther
from app.auth import Auther
from app.models.user import User, SignupForm, UserDAO
from app.utils.auth import is_authorized

auther = Auther()

@router.get(
    "/users/{revcat_id}",
    # dependencies=[Depends(is_authorized)],
)
async def get_user_by_id(
    revcat_id: str,
    # authorization: str = Header(),
):
    # user_id = auther.get_user_from_jwt(authorization)
    user: User = await User.find_one(User.revcat_id == revcat_id)
    if user is None:
        raise HTTPException(404)
    return UserDAO.parse_obj(user)

# # TODO require assertion of userDAO against authorization claim
# @router.put(
#     "/users",
#     dependencies=[Depends(is_authorized)],
# )
# async def update_user(
#     authorization: str = Header(),
#     userDAO: UserDAO = Body(),
# ):
#     user_id = auther.get_user_from_jwt(authorization)
#     userFromAuth: User = await User.get(user_id)
#     if userFromAuth is None:
#         raise HTTPException(404)
#     user = await User.find_one(User.email == userDAO.email)
#     if user.email != userFromAuth.email:
#         raise HTTPException(404)
#     fields = []
#     for key in userDAO.__dict__:
#         if key != "id" or key != "revision_id":
#             await user.update({"$set": { key : userDAO.__dict__[key] }})
#     newUser = await User.find_one(User.email == userDAO.email)
#     return UserDAO.parse_obj(newUser)

@router.post("/users")
async def add_user(
    signup_form: SignupForm = Body(),
):
    existing_user = await User.find_one(User.revcat_id == signup_form.revcat_id)
    if existing_user is not None:
        raise HTTPException(401)
    jwt_secret_key = token_urlsafe(64)
    new_user = User(
        revcat_id=signup_form.revcat_id,
        jwt_secret_key=jwt_secret_key,
        nativeLanguage=signup_form.nativeLanguage,
        studyLang=signup_form.studyLang,
    )
    inserted_user = await new_user.insert()
    return UserDAO.parse_obj(inserted_user)

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
