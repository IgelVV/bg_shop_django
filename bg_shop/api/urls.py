from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path("", include("account.urls")),
    path("", include("payment.urls")),
    path("", include("shop.urls")),
]
