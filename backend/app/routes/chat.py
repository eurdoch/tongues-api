from fastapi import (
    APIRouter,
    File,
    Header,
    HTTPException,
    Depends,
)
from pydantic import BaseModel
import os

import openai
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

from app.utils.auth import is_authorized
from app.models.completion import Model

from dotenv import load_dotenv
load_dotenv()

class CompletionRequest(BaseModel):
    prompt: str
    section: str
    language: str

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

openai.api_key = os.getenv('OPENAI_API_KEY')

@router.post(
    "/chat"
)
async def get_chat_response(
    completionRequest: CompletionRequest,
):
    

    system_template = """You are a {language} teacher who checks if the grammar of {language}
    sentences is correct.  A user will pass in a sentence and you will check the grammar.
    ONLY return either Yes or No
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{sentence}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    llm = ChatOpenAI()
    chain = LLMChain(
        llm=llm,
        prompt=chat_prompt,
    )
    response = chain.run(sentence=completionRequest.prompt, language=completionRequest.language)
    match response.replace('.', ''):
        case "No":
            system_template = """You are a translator who helps check the grammar of the {language} language."""
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
            human_template = """Explain the problems of the sentence {sentence} in the {language} language."""
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
            chain = LLMChain(
                llm=llm,
                prompt=chat_prompt,
            )
            response = chain.run(sentence=completionRequest.prompt, language=completionRequest.language)
            return {
                "grammar_correct": False,
                "response": response,
            }
        case "Yes":
            # model = await Model.find_one(
            #     Model.section == completionRequest.section,
            #     Model.language == completionRequest.language,
            # )
            system_template = """You are {language} person having a friendly conversation
            with a young man.  
            ONLY respond as if you are having a conversation with a friend.
            """
            human_template = "{sentence}"
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt, system_message_prompt])
            chain = LLMChain(
                llm=ChatOpenAI(),
                prompt=chat_prompt,
            )
            response = chain.run(sentence = completionRequest.prompt, language=completionRequest.language)
            return {
                "grammar_correct": True,
                "response": response
            }
        case _:
            raise Exception("Chat model did not return a valid response.")
