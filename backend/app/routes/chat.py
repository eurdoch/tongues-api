from fastapi import (
    Header,
    Body,
    APIRouter,
    Depends,
    Query,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from firebase_admin import auth

from app.models.user import User
from app.utils.auth import is_authorized
from app.utils.chat import get_chat_response_by_language
from app.utils.models import get_chat_response

class Conversation(BaseModel):
    text: str
    studyLang: str
    nativeLang: str
    history: str = None
    difficulty: str = "Beginner"

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
async def get_convo_response(
    authorization: str = Header(),
    conversation: Conversation = Body(),
):
    token = authorization.split(' ')[1]
    decoded_token = auth.verify_id_token(token)
    user: User = await User.find_one(User.firebase_user_id == decoded_token['uid'])
    if user.messageCount > 5 and not user.subscribed:
        return False
    if user is None:
        raise HTTPException(401)
    user.messageCount += 1
    await user.save()
    return get_chat_response_by_language(
        text=conversation.text,
        language=conversation.studyLang,
        history=conversation.history,
        difficulty=conversation.difficulty,
    )

@router.get(
    "/question"
)
async def get_answer(prompt: str = Query()):
    answer = get_chat_response(prompt, temperature=0.2)
    return { 'answer': answer }

#@router.get(
#    "/question"
#)
#async def ask_question(prompt: str = Query()):
#    return StreamingResponse(get_streaming_chat_response(prompt), media_type='text/event-stream')

