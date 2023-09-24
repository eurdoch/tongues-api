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
    PromptTemplate,
)
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

from app.utils.auth import is_authorized
from app.app import llm

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
                sentence=conversation.sentence, 
                study_language=conversation.studyLang,
                native_language=conversation.nativeLang,
            )
            return {
                "grammar_correct": False,
                "response": response,
            }
        case "Yes":
            memory = ConversationBufferMemory()
            if conversation.history is not None:
                messages = conversation.history.split('\n')
                messages = messages[:10] if len(messages) > 10 else messages
                for message in messages:
                    speaker, text = message.split(':')
                    if speaker == "Human":
                        memory.chat_memory.add_user_message(text[1:])
                    elif speaker == "AI":
                        memory.chat_memory.add_ai_message(text[1:])
            template = """You are {language} person having a friendly conversation in {language}.

            Current conversation:
            {history}
            Human: {input}
            AI:"""
            prompt_template = PromptTemplate(input_variables=["history", "input", "language"], template=template)

            conversation_chain = ConversationChain(
                llm=llm,
                prompt=prompt_template.partial(language=conversation.studyLang),
                verbose=True,
                memory=memory
            )
            response = conversation_chain.predict(input=conversation.sentence)
            history = conversation_chain.memory.buffer_as_str

            return {
                "grammar_correct": True,
                "history": history,
                "response": response
            }
        case _:
            raise Exception("Chat model did not return a valid response.")
