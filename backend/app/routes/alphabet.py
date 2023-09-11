from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Depends,
)

from app.utils.auth import is_authorized
from app.models.alphabet import Alphabet, Letter
from app.app import app

from bson import ObjectId

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

# Require admin priv
@router.post(
    "/alphabet"
)
async def add_alphabet(
    alphabet: Alphabet,
) -> Alphabet:
    return await alphabet.insert()

# Require admin priv
@router.delete(
    "/alphabet/{language}"
)
async def delete_alphabet(
    language: str,
):
    alphabet = await Alphabet.find_one(Alphabet.language == language)
    for letter in alphabet.letters:
        await app.audio_bucket.delete(ObjectId(letter.audio_id))
    await alphabet.delete()

@router.get(
    "/alphabet/{language}"
)
async def get_alphabet(
    language: str,
) -> Alphabet:
    return await Alphabet.find_one(Alphabet.language == language)
