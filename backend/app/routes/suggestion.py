from fastapi import (
    APIRouter,
    Depends,
)
import json
from pydantic import BaseModel

import openai

from app.utils.auth import is_authorized
from app.utils.models import get_chat_response

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
        response = get_chat_response(f"Generate 3 suggestions for starting a conversation in {suggestionRequest.language}.  ONLY return the suggestions as a JSON object of the form {{ suggestions: ... }}")
        return json.loads(response.replace('\n', ''))
    else:
        response = get_chat_response(f"Generate 3 suggestions for continuing the following conversation in {suggestionRequest.language}.  ONLY return the suggestions as a JSON object of the form {{ suggestions: ... }}. Conversation: {suggestionRequest.history}")
        return json.loads(response.replace('\n', ''))
