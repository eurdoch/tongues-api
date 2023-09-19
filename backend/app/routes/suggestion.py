from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Depends,
)
from typing import Union
import os

from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

from app.app import app
from app.utils.auth import is_authorized
from app.models.example import Example
from app.models.completion import Model

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
):
    llm = OpenAI(model_name='gpt-3.5-turbo-instruct')
    if prompt == None:
        system_template = """You are a {language} translator who gives suggestions
        for sentences to use in conversation.
        ONLY return a comma separated list of the sentences.
        """
        human_template = """
        Give me three sentences for starting a conversation in {language}.
        """
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            human_message_prompt
        ])
        chain = LLMChain(
            llm=llm,
            prompt=chat_prompt
        )
        return {
            "response": chain.run(language=language),
        }
