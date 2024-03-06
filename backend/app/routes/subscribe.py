from fastapi import (
    Body,
    APIRouter,
    Request,
    Query,
    Header,
    HTTPException
)
from pydantic import BaseModel
from firebase_admin import auth

import stripe
stripe.api_key="sk_test_51OodJFB8zNt1mTxfFmNgXsMqscUAwN7ZjNYx8ChvR0olpFqVS6xLj75AW4gkgHnLOAxQOhJlg3pN7BzGo0DT0RCa003UxSbakv"

from app.models.user import User

class Subscription(BaseModel):
    priceId: str

router = APIRouter(
    prefix="/api/v0",
)

@router.get("/success")
async def checkout_success(
    authorization = Header(),
    session_id: str = Query(),
):
    session = stripe.checkout.Session.retrieve(session_id)
    if session["status"] == "complete" and session["payment_status"] == "paid":
        token = authorization.split(' ')[1]
        decoded_token = auth.verify_id_token(token)
        user: User = await User.find_one(User.firebase_user_id == decoded_token['uid'])
        if user is None:
            raise HTTPException(401)
        user.subscribed = True
        user.stripeCustomerId = session["customer"]
        await user.save()
        return session
    else:
        return False
    return False

@router.post(
    "/create-checkout-session"
)
async def create_checkout_subscription(
    authorization = Header(),
    subscription: Subscription = Body()
):
    token = authorization.split(' ')[1]
    decoded_token = auth.verify_id_token(token)
    custom_token = auth.create_custom_token(decoded_token['uid'])
    session = stripe.checkout.Session.create(
        success_url='https://tongues.media/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='https://tongues.media/checkout',
        mode='subscription',
        line_items=[{
            'price': subscription.priceId,
            'quantity': 1,
        }],
    )
    return {
        "custom_token": custom_token,
        "redirect_url": session.url,
    }

@router.post("/stripewebhook")
async def webhook_received(request: Request):
    webhook_secret = 'whsec_dMd5xYddSNDbOdeNdn0uu5Kigdm1Hszv'
    request_data = await request.json()

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
          event = stripe.Webhook.construct_event(
              payload=request.data, sig_header=signature, secret=webhook_secret)
          data = event['data']
        except Exception as e:
          return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    if event_type == 'checkout.session.completed':
        # Payment is successful and the subscription is created.
        # You should provision the subscription and save the customer ID to your database.
        print(data)
    elif event_type == 'invoice.paid':
        # Continue to provision the subscription as payments continue to be made.
        # Store the status in your database and check when a user accesses your service.
        # This approach helps you avoid hitting rate limits.
        print(data)
    elif event_type == 'invoice.payment_failed':
        # The payment failed or the customer does not have a valid payment method.
        # The subscription becomes past_due. Notify your customer and send them to the
        # customer portal to update their payment information.
        print(data)
    else:
        print('Unhandled event type {}'.format(event_type))
