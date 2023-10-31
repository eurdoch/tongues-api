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

class Conversation(BaseModel):
    text: str
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

@router.post(
    "/chat"
)
async def get_chat_response(
    conversation: Conversation,
):
    return get_chat_response_by_language(
        text=conversation.text,
        language=conversation.studyLang,
        history=conversation.history
    )

# For debug purposes
#@router.post(
#    "/grammar"
#)
#async def check_grammar(
#    sentence: Sentence
#):
#    return is_valid_grammar(text=sentence.text, language=sentence.language)
