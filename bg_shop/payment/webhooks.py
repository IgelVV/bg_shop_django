import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from payment import models


@csrf_exempt
def stripe_webhook(request):
    body_unicode = request.body.decode('utf-8')
    payload = json.loads(body_unicode)
    sign = payload.get('PAYMENT_SERVICE_SIGNATURE', None)
    if sign != settings.PAYMENT_SERVICE_SIGNATURE:
        return HttpResponse(status=400)

    status = payload.get("status", None)
    order_id = payload.get("order_id", None)
    errors = payload.get("errors", None)

    if status == "success":
        order = Order.objects.get(pk=order_id)
        order.paid = True
        order.full_clean()
        order.save()
        payment = models.Payment(
            order_id=order_id, payment_id=f"{order_id}test")
        payment.full_clean()
        payment.save()
    return HttpResponse(status=200)
