from django.urls import path

from orders import apis

app_name = "orders"

urlpatterns = [
    path('basket/', apis.CartApi.as_view(), name="basket"),  # GET POST DELETE
    # path('orders/', views., name=""),  #GET POST
    # path('orders/<int:id>/', views., name=""),  #GET POST
]
