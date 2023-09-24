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
    sentence: str
    studyLang: str
    nativeLang: str
    history: str = None

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
        sentence=conversation.sentence, 
        study_language=conversation.studyLang
    )
    print(response)
    match response.replace('.', ''):
        case "No":
            system_template = """You are a language teacher who helps check the grammar of the {study_language} language."""
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
            human_template = """Explain the problems of the grammar in sentence "{sentence}" in 
            the {study_language} language, using the {native_language} to explain.
            """
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
            chain = LLMChain(
                llm=llm,
                prompt=chat_prompt,
            )
            response = chain.run(
                sentence=conversation.sentence, 
                study_language=conversation.studyLang,
                native_language=conversation.nativeLang,
            )
            return {
                "grammar_correct": False,
                "response": response,
                "history": "",
            }
        case "Yes":
            return get_chat_response_by_language(
                sentence=conversation.sentence,
                language=conversation.studyLang,
                history=conversation.history
            )
        case _:
            raise Exception("Chat model did not return a valid response.")
