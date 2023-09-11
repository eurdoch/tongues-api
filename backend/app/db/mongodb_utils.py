from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie

from .mongodb import db
from ..core.config import MONGODB_URL, TESTING
from ..api.models.user import User

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(MONGODB_URL)
    await init_beanie(
        database=db.client.glosso,
        document_models=[
            User,
        ]
    )

async def close_mongo_connection():
    db.client.close()