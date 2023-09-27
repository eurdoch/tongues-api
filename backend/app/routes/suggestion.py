from fastapi import (
    APIRouter,
    Depends,
)
import json
from pydantic import BaseModel

import openai

from app.utils.auth import is_authorized

from dotenv import load_dotenv
load_dotenv()

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

class SuggestionRequest(BaseModel):
    language: str
    history: str = None

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

@router.post(
    "/suggestions"
)
async def get_suggestions(
    suggestionRequest: SuggestionRequest,
):
    if suggestionRequest.history == None:
        prompt = f"""You are a {suggestionRequest.language} translator who gives suggestions
        for sentences to use in conversation. The user will input a language and you will
        return three simple sentences for initiating a conversation 
        in that language.
        ONLY return a json string with the key suggestions and the value as list of the suggestions.
        """
        
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "user", "content": prompt}],
            functions=suggestion_functions,
            function_call="auto",
        )
        output = response.choices[0].message.function_call.arguments
        return json.loads(output.replace('\n', ''))
    else:
        prompt = f"""You are a {suggestionRequest.language} teacher who gives suggestions for sentences to 
        use in conversation. Given the conversation
        
        {suggestionRequest.history}
        Human:

        give 3 suggestions for how to complete the last statement from the human.
        """
        
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "user", "content": prompt}],
            functions=suggestion_functions,
            function_call="auto",
        )
        output = response.choices[0].message.function_call.arguments
        return json.loads(output.replace('\n', ''))
