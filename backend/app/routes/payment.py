from fastapi import (
    APIRouter,
    HTTPException,
    Body,
    Form,
    Query,
    Request,
)
from app.models.user import User
from typing import Annotated
from fastapi.responses import RedirectResponse
import stripe
import os

stripe.api_key = os.environ.get("STRIPE_API_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

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

@router.get(
    '/customer'
)
async def get_customer_info(
    session_id: str = Query(),
):
    checkout_session = stripe.checkout.Session.retrieve(session_id)
    return checkout_session.customer

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

@router.post(
    '/webhook'
)
async def handle_webhook_update(
    request: Request,
):
    payload = await request.body()
    signature = request.headers['stripe-signature']
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=webhook_secret
        )
        event_type = event['type']
        user: User = await User.find_one(User.email == event['data']['object']['customer_email'])

        if user is None:
            raise Exception(404)
        if event_type == 'checkout.session.completed':
            user.subscription = 'active'
            await user.save()
        elif event_type == 'invoice.paid':
            user.subscription = 'active'
            await user.save()
        elif event_type == 'invoice.payment_failed':
            user.subscription = 'inactive'
            await user.save()
    except Exception as e:
        print(e)
        return e
