from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from contextlib import asynccontextmanager

from langchain.chat_models import ChatOpenAI

from app.config import CONFIG
from app.models.user import User, UserDAO
from app.models.example import Example
from app.models.translate import Word
from app.models.completion import Model
from app.models.alphabet import Alphabet

from dotenv import load_dotenv
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db = AsyncIOMotorClient(CONFIG.mongo_uri).grawk
    app.audio_bucket = AsyncIOMotorGridFSBucket(app.db, bucket_name='audio')
    await init_beanie(
        app.db, 
        document_models=[
            User,
            UserDAO,
            Example,
            Word,
            Model,
            Alphabet,
        ]
    )
    yield

app = FastAPI(
    lifespan=lifespan,
)

llm = ChatOpenAI()
