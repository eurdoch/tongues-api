from fastapi import (
    APIRouter,
    File,
    Header,
    HTTPException,
    Depends,
)
from pydantic import BaseModel
import openai
import os

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
    "/completions"
)
async def get_completion(
    completionRequest: CompletionRequest,
):
    model = await Model.find_one(Model.section == completionRequest.section, Model.language == completionRequest.language)
    completion = openai.ChatCompletion.create(
        model=model.name,
        messages=[
            {"role": "user", "content": completionRequest.prompt}
        ]
    )
    return {
        "response": completion.choices[0].message.content,
    }
