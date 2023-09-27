from fastapi import (
    APIRouter,
    File,
    Header,
    HTTPException,
    Depends,
)
from pydantic import BaseModel

from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    PromptTemplate,
)
from langchain.chains import LLMChain

from app.utils.auth import is_authorized
from app.app import llm
from app.utils.chat import get_chat_response_by_language
from app.utils.chat import check_text_grammar

class Conversation(BaseModel):
    sentence: str
    studyLang: str
    nativeLang: str
    history: str = None

class Sentence(BaseModel):
    text: str
    language: str

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

MISUNDERSTOOD_RESPONSE = {
    "Dutch": "Het spijt me, ik begreep je niet.",
    "English": "Sorry, I didn't understand you.",
    "French": "Je suis désolé, je ne t'ai pas compris.",
    "Spanish": "Lo siento, no te entendí.",
    "Italian": "Mi dispiace, non ti ho capito.",
    "German": "Es tut mir leid, ich habe dich nicht verstanden."
}

@router.post(
    "/chat"
)
async def get_chat_response(
    conversation: Conversation,
):
    return get_chat_response_by_language(
        sentence=conversation.sentence,
        language=conversation.studyLang,
        history=conversation.history
    )

@router.post(
    "/grammar"
)
async def check_grammar(
    sentence: Sentence
):
    return check_text_grammar(text=sentence.text, language=sentence.language)
