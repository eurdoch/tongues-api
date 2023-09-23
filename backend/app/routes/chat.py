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
    studyLang: str
    nativeLang: str

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

openai.api_key = os.getenv('OPENAI_API_KEY')

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
    completionRequest: CompletionRequest,
):
    llm = ChatOpenAI()
    # human_template = """Does the sentence {sentence} make sense in {language}? 
    # ONLY reply with Yes or No
    # """
    # human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    # chat_prompt = ChatPromptTemplate.from_messages([
    #     human_message_prompt,
    # ])
    # chain = LLMChain(
    #     llm=llm,
    #     prompt=chat_prompt
    # )
    # response = chain.run(language=completionRequest.language, sentence=completionRequest.prompt)
    # if response.replace('.', '') == "No":
    #     return {
    #         "grammar_correct": True,
    #         "response": MISUNDERSTOOD_RESPONSE[completionRequest.language]
    #     }

    system_template = """You are a {study_language} teacher who checks if the grammar of 
    {study_language} sentences is correct.  A user will pass in a sentence and you will check the grammar.
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
    response = chain.run(
        sentence=completionRequest.prompt, 
        study_language=completionRequest.studyLang
    )
    match response.replace('.', ''):
        case "No":
            system_template = """You are a translator who helps check the grammar of the {study_language} language."""
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
            human_template = """Explain the problems of the grammar in {study_language} sentence "{sentence}" using 
            the {native_language} language.
            """
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
            chain = LLMChain(
                llm=llm,
                prompt=chat_prompt,
            )
            response = chain.run(
                sentence=completionRequest.prompt, 
                study_language=completionRequest.studyLang,
                native_language=completionRequest.nativeLang,
            )
            return {
                "grammar_correct": False,
                "response": response,
            }
        case "Yes":
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
            response = chain.run(sentence = completionRequest.prompt, language=completionRequest.studyLang)
            return {
                "grammar_correct": True,
                "response": response
            }
        case _:
            raise Exception("Chat model did not return a valid response.")
