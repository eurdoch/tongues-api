from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.utils.auth import is_authorized
from app.utils.chat import get_chat_response_by_language, get_answer
from app.utils.models import get_streaming_chat_response

class Conversation(BaseModel):
    text: str
    studyLang: str
    nativeLang: str
    history: str = None
    difficulty: str = "beginner"


class Sentence(BaseModel):
    text: str
    language: str

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

@router.post(
    "/chat"
)
async def get_chat_response(
    conversation: Conversation,
):
    return get_chat_response_by_language(
        text=conversation.text,
        language=conversation.studyLang,
        history=conversation.history,
        difficulty=conversation.difficulty,
    )

@router.get(
    "/question"
)
async def ask_question(prompt: str = Query()):
    return StreamingResponse(get_streaming_chat_response(prompt), media_type='text/event-stream')
