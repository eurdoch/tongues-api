from fastapi import (
    APIRouter,
    Depends,
)
import json
from pydantic import BaseModel

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
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

class SuggestionRequest(BaseModel):
    language: str
    history: str = None

instruct_llm = ChatOpenAI(model="gpt-3.5-turbo-instruct")

@router.post(
    "/suggestions"
)
async def get_suggestions(
    suggestionRequest: SuggestionRequest,
):
    if suggestionRequest.history == None:
        system_template = """You are a {language} translator who gives suggestions
        for sentences to use in conversation. The user will input a language and you will
        return three simple sentences under four words for initiating a conversation 
        in that language.
        ONLY return a json string with the key suggestions.
        """
        human_template = "{language}"
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
        response = chain.run(language=suggestionRequest.language)
        return json.loads(response.replace('\n', ''))
    else:
        system_template = """You are a {language} translator who gives suggestions
        for sentences to use in conversation. The user will input a conversation and you will
        return three simple sentences as suggestions that the Human would respond with.
        ONLY return a json string with the key suggestions and the value as list of the 
        suggestions.
        """
        human_template = "{history}"
        print(suggestionRequest.history)
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            human_message_prompt
        ])
        chain = LLMChain(
            llm=instruct_llm,
            prompt=chat_prompt
        )
        response = chain.run(
            language=suggestionRequest.language, 
            history=suggestionRequest.history
        )
        print(response)
        return json.loads(response.replace('\n', ''))
