from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Depends,
)
from typing import Union

import openai
import os

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

openai.api_key = os.getenv('OPENAI_API_KEY')

# Change to use query paramters instead of Path
@router.get(
    "/suggestions"
)
async def get_suggestions(
    section: str, # Query
    language: str, # Query
    prompt: Union[str, None] = None, # Query
):
    suggestions = []
    if prompt is None:
        examples = await Example.find(
            Example.section == section, Example.language == language
        ).to_list()
        for example in examples[0:3]:
            suggestions.append({
                'sentence': example.conversation[0].sentence,
                'audio_id': str(example.conversation[0].audio_id),
            })
        return suggestions
    else:
        model = await Model.find_one(
            Model.section == section,
            Model.language == language
        )
        for i in range(0, 3):
            completion = openai.ChatCompletion.create(
                model=model.name,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            suggestions.append({
                'sentence': completion['choices'][0]['message']['content'],
                'audio_id': None,
            })
        return suggestions
