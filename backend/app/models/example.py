from beanie import Document
from beanie import PydanticObjectId
from pydantic import BaseModel
from typing import List

class Sentence(BaseModel):
    sentence: str
    audio_id: PydanticObjectId
    
class Example(Document):
    section: str
    conversation: List[Sentence]
    language: str