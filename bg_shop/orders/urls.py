from django.urls import path

from orders import apis

app_name = "orders"

urlpatterns = [
    # GET POST DELETE
    path('basket/', apis.CartApi.as_view(), name="basket"),
    # GET POST: get all (active) orders as history, post - create order
    path('orders/', apis.OrdersApi.as_view(), name="orders"),
    # GET POST: post - confirm
    path(
        'orders/<int:id>/',
        apis.OrderDetailApi.as_view(),
        name="order_detail"
    ),
]
