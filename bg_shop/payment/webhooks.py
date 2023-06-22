import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from payment import models, enums


@csrf_exempt
def stripe_webhook(request):
    payload = json.loads(request.body)
    sign = payload.get('PAYMENT_SERVICE_SIGNATURE', None)
    if sign != settings.PAYMENT_SERVICE_SIGNATURE:
        return HttpResponse(status=403)

    status = payload.get("status", None)
    order_id = payload.get("order_id", None)
    errors = payload.get("errors", None)
    payment_id = payload.get("payment_id", None)

    order = Order.objects.get(pk=order_id)
    if order.paid:
        return HttpResponse(status=409)

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
            order.status = Order.Statuses.REJECTED
            order.full_clean()
            order.save()
        case _:
            return HttpResponse(status=400)
    return HttpResponse(status=200)
