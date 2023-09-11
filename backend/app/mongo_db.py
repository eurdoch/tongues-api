import secrets
import io
from bson.objectid import ObjectId
from app.api.models.user import User

from motor.motor_asyncio import AsyncIOMotorClient

from app.auth import Auther
from exception import UserAlreadyExistsException

class DbClient:
    def __init__(self, url='mongodb://localhost:27017'):
        self.client = AsyncIOMotorClient(url)

    def get_client(self):
        return self.client

class Db:
    # TODO create DbClient in __init__ instead of calling class constructor
    def __init__(self, db_name='langtools'):
        self.db = DbClient().get_client()[db_name]
        self.auther = Auther()

    async def find_by_username(self, username: str):
        user = await self.db.users.find_one({'username': username})
        if user is None:
            return None
        user['_id'] = str(user['_id'])
        return user

    async def find_by_email(self, email: str):
        user = await self.db.users.find_one({'email': email})
        if user is None:
            return None
        user['_id'] = str(user['_id'])
        return user

    async def find_by_id(self, _id: str):
        user = await self.db.users.find_one({'_id': ObjectId(_id)})
        return None if user is None else user

    async def add_user(self, user) -> bool:
        """
        Method for adding user to database.  Accepts a user,
        then checks if users exists otherwise raises an 
        Exception.  

        If user does not exist, it generates a secret key
        for JWT generation, calls insert of Db object
        and if successful returns access_token, otherwise
        an Exception is raised

        Returns: True if user inserted, False otherwise  
        """
        returned_user = await self.db.users.find_one(
            {'email': user['email']}
        )
        if returned_user is not None:
            raise UserAlreadyExistsException()
        
        user['jwt_secret_key'] = self.auther.get_new_jwt_secret()
        result = await self.db.users.insert_one(user)
        return result.acknowledged

    async def update_user(self, userDAO) -> bool:
        result = await self.db.users.update_one(
            {"_id": userDAO["_id"]},
            {"$set": userDAO.dict() }
        )
        return result.acknowledged

    async def delete_user(self, email) -> bool:
        result = await self.db.users.delete_one({"email": email})
        return result.acknowledged

    async def update_jwt_secret(self, email) -> str | None:
        jwt_secret_key = secrets.token_urlsafe(64)
        result = await self.db.users.update_one(
            {'email': email},
            {'$set': {'jwt_secret_key': jwt_secret_key}}
        )
        return jwt_secret_key if result.modified_count == 1 else None
