from django.urls import path

from payment import apis

app_name = "payment"

urlpatterns = [
    path('payment/<int:id>/', apis.PaymentApi.as_view(), name="payment"),  # POST
]
