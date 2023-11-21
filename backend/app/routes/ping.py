from fastapi import (
    APIRouter, 
)

router = APIRouter(
    prefix="/api/v0",
)

@router.get("/ping")
async def ping():
    return {
        "message": "ponged",
    }
