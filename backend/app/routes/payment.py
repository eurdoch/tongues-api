from fastapi import (
    APIRouter,
    HTTPException,
    Body,
    Form,
    Query,
)
from typing import Annotated
from fastapi.responses import RedirectResponse
import stripe
import os
stripe.api_key = os.environ.get("STRIPE_API_KEY")

router = APIRouter(
    prefix="/api/v0"
)

@router.post(
    "/create-checkout-session",
)
async def create_checkout_session(
    customer_email: Annotated[str, Form()],
    lookup_key: Annotated[str, Form()],
):
    try:
        prices = stripe.Price.list(
            lookup_keys=['grawk_monthly_subscription'],
            expand=['data.product']
        )

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': prices.data[0].id,
                    'quantity': 1,
                }
            ],
            subscription_data={
                "trial_period_days": 3,
            },
            customer_email=customer_email,
            mode='subscription',
            success_url='https://langtools.link/success?success=true&session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://langtools.link/success?canceled=true',
        )
        return RedirectResponse(url=checkout_session.url, status_code=303)
    except Exception as e:
        print(e)
        return "Server error", 500

@router.post(
    '/create-portal-session'
)
async def create_portal_session(
    session_id: str = Query(),
):
    checkout_session = stripe.checkout.Session.retrieve(session_id)

    return_url = 'https://langtools.link/settings/subscription'

    portal_session = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=return_url,
    )
    return RedirectResponse(url=portal_session.url, status_code=303)
