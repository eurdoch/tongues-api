from fastapi import (
    APIRouter,
    Depends,
)
import json
from pydantic import BaseModel

import openai

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

@router.post(
    "/suggestions"
)
async def get_suggestions(
    suggestionRequest: SuggestionRequest,
):
    if suggestionRequest.history == None:
        pass
        # system_template = """You are a {language} translator who gives suggestions
        # for sentences to use in conversation. The user will input a language and you will
        # return three simple sentences under four words for initiating a conversation 
        # in that language.
        # ONLY return a json string with the key suggestions.
        # """
        # human_template = "{language}"
        # system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        # human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        # chat_prompt = ChatPromptTemplate.from_messages([
        #     system_message_prompt,
        #     human_message_prompt
        # ])
        # chain = LLMChain(
        #     llm=llm,
        #     prompt=chat_prompt
        # )
        # response = chain.run(language=suggestionRequest.language)
        # return json.loads(response.replace('\n', ''))
    else:
        prompt = f"""You are a English {suggestionRequest.language} who gives suggestions for sentences to 
        use in conversation. The user will input a conversation and you will return three 
        simple sentences as suggestions that the Human would respond with.
        ONLY return a json string with the key suggestions and the value as list of the suggestions.
        
        Conversation: {suggestionRequest.history}
        """
        suggestion_functions = [
            {
                'name': 'extract_suggestions',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'suggestions': {
                            'type': 'array',
                            'items': {
                                'type': 'string'}
                            }
                    }
                }
            }
        ]
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "user", "content": prompt}],
            functions=suggestion_functions,
            function_call="auto",
        )
        return json.loads(response.replace('\n', ''))
