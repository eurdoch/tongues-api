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

llm = ChatOpenAI()

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
    chain = LLMChain(
        llm=llm,
        prompt=chat_prompt,
    )
    response = chain.run(sentence=completionRequest.prompt, language=completionRequest.language)
    print(response)
    match response:
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
            system_template = """You are a young Colombian woman talking to her boyfriend.  Return a response as if you are holding a conversation."""
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
            human_template = "{sentence}"
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
            chain = LLMChain(
                llm=llm,
                prompt=chat_prompt,
            )
            response = chain.run(sentence = completionRequest.prompt, language=completionRequest.language)
            return {
                "grammar_correct": True,
                "response": response
            }
        case _:
            raise Exception("Chat model did not return a valid response.")
    # model = await Model.find_one(Model.section == completionRequest.section, Model.language == completionRequest.language)
    # completion = openai.ChatCompletion.create(
    #     model=model.name,
    #     messages=[
    #         {"role": "user", "content": completionRequest.prompt}
    #     ]
    # )
    # return {
    #     "response": completion.choices[0].message.content,
    # }
