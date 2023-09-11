from beanie import Document
from typing import List
from beanie import PydanticObjectId
from pydantic import BaseModel

class Letter(BaseModel):
    text: str
    audio_id: PydanticObjectId

class Alphabet(Document):
    letters: List[Letter]
    language: str