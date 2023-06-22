import requests

from decimal import Decimal
from celery import shared_task
from django.conf import settings

from payment import enums


@shared_task
def third_party_payment_service(
        url: str, order_id: int, card_number: str, payment: Decimal):
    """
    Imitation of handling by payment service.
    """
    headers = {'PAYMENT_SERVICE_SIGNATURE': settings.PAYMENT_SERVICE_SIGNATURE}
    body = {
        "PAYMENT_SERVICE_SIGNATURE": settings.PAYMENT_SERVICE_SIGNATURE,
        "order_id": order_id,
        "status": "",
        "errors": [],
        "payment_id": f"{order_id}test_payment_id"
    }

    if len(card_number) != 8:
        raise ValueError("Card number must contain 8 digits")
    card_number = int(card_number)
    if (card_number % 2 == 0) and (card_number % 10 != 0):
        body["status"] = enums.PaymentStatuses.SUCCESS
    else:
        body["status"] = enums.PaymentStatuses.FAIL
        body["errors"].append("wrong number")

    response = requests.post(url, json=body, headers=headers)
    print(response)


