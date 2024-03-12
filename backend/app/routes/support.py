from fastapi import (
    APIRouter, 
    Body,
    HTTPException,
    Header,
)
from datetime import datetime
from pydantic import BaseModel

from firebase_admin import auth

from app.utils.auth import is_authorized

router = APIRouter(
    prefix="/api/v0",
)

from app.models.user import User, SupportTicket
from app.utils.auth import is_authorized

class SupportMessage(BaseModel):
	email: str
	message: str

@router.post("/support")
async def support_ticket(
	supportMessage: SupportMessage = Body(),
    authorization = Header(),
):
    token = authorization.split(' ')[1]
    decoded_token = auth.verify_id_token(token)
    user: User = await User.find_one(User.firebase_user_id == decoded_token['uid'])
    if user is None:
        raise HTTPException(401)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket = SupportTicket(
        email=supportMessage.email,
        message=supportMessage.message,
        user=user,
        date=now,
    )
    inserted_ticket = await ticket.insert()
    return {
        'ticket_id': str(inserted_ticket.id)
    }
