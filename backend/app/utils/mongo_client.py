import os
from motor.motor_asyncio import AsyncIOMotorClient

mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))

def get_client():
    return mongo_client