import requests

from decimal import Decimal
from celery import shared_task
from django.urls import reverse
from django.conf import settings


@shared_task
def third_party_payment_service(
        url: str, order_id: int, card_number: str, payment: Decimal):
    """
    Imitation of handling by payment service.
    """
    headers = {'PAYMENT_SERVICE_SIGNATURE': settings.PAYMENT_SERVICE_SIGNATURE}
    body = {
        'PAYMENT_SERVICE_SIGNATURE': settings.PAYMENT_SERVICE_SIGNATURE,
        "order_id": order_id,
        "status": "",
        "errors": [],
    }

    if len(card_number) != 8:
        raise ValueError("Card number must contain 8 digits")
    card_number = int(card_number)
    if (card_number % 2 == 0) and (card_number % 10 != 0):
        body["status"] = "success"
    else:
        body["status"] = "fail"
        body["errors"].append("wrong number")

    response = requests.post(url, json=body, headers=headers)
    print(response)


