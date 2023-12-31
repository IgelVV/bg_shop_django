"""Payment system webhooks."""

import json

from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from orders import models as order_models
from orders import services as order_services
from payment import models, enums


@csrf_exempt
def payment_webhook(request: HttpRequest) -> HttpResponse:
    """
    Handle request from payment system.

    If success, creates Payment for Order and set Order.paid to True,
    otherwise rejects order.
    :param request: call from payment system after handling payment.
    :return: response for payment system.
    """
    payload = json.loads(request.body)
    sign = payload.get('PAYMENT_SERVICE_SIGNATURE', None)
    if sign != settings.PAYMENT_SERVICE_SIGNATURE:
        return HttpResponse(status=403)

    status = payload.get("status", None)
    order_id = payload.get("order_id", None)
    # errors = payload.get("errors", None)
    payment_id = payload.get("payment_id", None)

    order = order_models.Order.objects.get(pk=order_id)
    if order.paid:
        return HttpResponse(status=409)
    with transaction.atomic():
        match status:
            case enums.PaymentStatuses.SUCCESS.value:
                order.paid = True
                order.full_clean()
                order.save()
                payment = models.Payment(
                    order_id=order_id,
                    payment_id=payment_id,)
                payment.full_clean()
                payment.save()
            case enums.PaymentStatuses.FAIL.value:
                order_services.OrderService().reject(order_id=order_id)
            case _:
                print(status)  # todo log
                return HttpResponse(status=400)
    return HttpResponse(status=200)
