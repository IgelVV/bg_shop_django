from django.urls import path

from payment import apis
from payment import webhooks

app_name = "payment"

urlpatterns = [
    path('payment/<int:id>/', apis.PaymentApi.as_view(), name="payment"),  # POST
    path('payment/webhook/', webhooks.stripe_webhook, name="payment-webhook"),  # POST
]
