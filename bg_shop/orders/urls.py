from django.urls import path

from orders import apis

app_name = "orders"

urlpatterns = [
    path('basket/', apis.CartApi.as_view(), name="basket"),  # GET POST DELETE
    path('orders/', apis.OrdersApi.as_view(), name="orders"),  #GET POST get all (active) orders as history, post - create order
    path('orders/<int:id>/', apis.OrderDetailApi.as_view(), name="order_detail"),  #GET POST post - confirm
]
