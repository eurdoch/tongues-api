from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Depends,
)
from typing import Union
import os
import json

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

from app.app import llm
from app.utils.auth import is_authorized
from app.utils.chat import get_suggestions_by_language

from dotenv import load_dotenv
load_dotenv()

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

# Change to use query paramters instead of Path
@router.get(
    "/suggestions"
)
async def get_suggestions(
    language: str, # Query
    prompt: Union[str, None] = None, # Query
    history: Union[str, None] = None,
):
    # if prompt == None:
    #     system_template = """You are a {language} translator who gives suggestions
    #     for sentences to use in conversation. The user will input a language and you will
    #     return three simple sentences under four words for starting a conversation in that language.
    #     ONLY return a json object with the key suggestions.
    #     """
    #     human_template = "{language}"
    #     system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    #     human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    #     chat_prompt = ChatPromptTemplate.from_messages([
    #         system_message_prompt,
    #         human_message_prompt
    #     ])
    #     chain = LLMChain(
    #         llm=llm,
    #         prompt=chat_prompt
    #     )
    #     response = chain.run(language=language)
    #     return json.loads(response.replace('\n', ''))
    # else:
    system_message = """You are a {language} teacher that gives suggestions
    for conversations in {language}.  Given the following conversation, 
    suggest a response to continue the conversation."""
    return get_suggestions_by_language(
        langauge=language,
        history=history,
        system_message=system_message
    )