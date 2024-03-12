from fastapi import (
    APIRouter, 
    Body,
    HTTPException,
    Header,
)
from datetime import datetime
from firebase_admin import auth

from app.utils.auth import is_authorized

router = APIRouter(
    prefix="/api/v0",
)

from app.models.user import User, SupportTicket
from app.utils.auth import is_authorized

@router.post("/support")
async def support_ticket(
    authorization = Header(),
    supportTicket: SupportTicket = Body(),
):
    token = authorization.split(' ')[1]
    decoded_token = auth.verify_id_token(token)
    user: User = await User.find_one(User.firebase_user_id == decoded_token['uid'])
    if user is None:
        raise HTTPException(401)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket = SupportTicket(
        email=supportTicket.email,
        message=supportTicket.message,
        user=user,
        date=now,
    )
    inserted_ticket = ticket.insert()
    return {
        ticket_id: inserted_ticket._id
    }
