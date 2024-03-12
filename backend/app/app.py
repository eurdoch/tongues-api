from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from contextlib import asynccontextmanager

from langchain.chat_models import ChatOpenAI
import firebase_admin
from firebase_admin import credentials

from app.config import CONFIG
from app.models.user import User, UserDAO, SupportTicket
from app.models.translate import Word

from dotenv import load_dotenv
load_dotenv()

import certifi
ca = certifi.where()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db = AsyncIOMotorClient(CONFIG.mongo_uri, tlsCAFile=ca).tongues
#    app.audio_bucket = AsyncIOMotorGridFSBucket(app.db, bucket_name='audio')
    await init_beanie(
        app.db, 
        document_models=[
            User,
            UserDAO, 
            SupportTicket,
        ]
    )
    yield

app = FastAPI(lifespan=lifespan)

cred = credentials.Certificate('./firebase_key.json')
firebase_admin.initialize_app(cred)
#llm = ChatOpenAI()
