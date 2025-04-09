from dataclasses import dataclass
from unittest.mock import patch

import pytest


@dataclass
class PaymentIntent:
    id: str
    client_secret: str
    amount: int
    currency: str
    status: str


@pytest.fixture
def mock_payment_intent():
    """
    Fixture that mocks Stripe PaymentIntent.create()
    """
    mock_intent = PaymentIntent(
        **{
            "id": "pi_test_123",
            "client_secret": "pi_test_secret_123",
            "amount": 2000,
            "currency": "usd",
            "status": "succeeded",
        }
    )

    with patch("stripe.PaymentIntent.create") as mock_create:
        mock_create.return_value = mock_intent
        yield mock_create


@pytest.fixture
def mock_webhook():
    """
    Fixture that mocks Stripe webhook
    """
    mock_event = {"type": {"payment_intent": "succeeded"}}

    with patch("stripe.Webhook.construct_event") as mock_construct:
        mock_construct.return_value = mock_event
        yield mock_construct
