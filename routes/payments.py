import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from db import get_db
from models import Order

router = APIRouter(prefix="/payments")

# Initialize Stripe
stripe.api_key = "your_stripe_secret_key"


@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, "your_stripe_webhook_secret"
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        order = (
            db.query(Order)
            .filter(Order.payment_intent_id == payment_intent["id"])
            .first()
        )

        if order:
            order.payment_status = "paid"
            order.status = "paid"

            # Update product stock
            for item in order.items:
                product = item.product
                product.stock -= item.quantity

            db.commit()

    return {"status": "success"}
