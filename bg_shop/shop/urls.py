from django.urls import path

from shop import apis

app_name = "shop"

urlpatterns = [
    path('categories/', apis.CategoryApi.as_view(), name="categories"),  #GET
    # path('catalog/', views., name="catalog"),  #GET ${category.id} POST # todo POST add spec to swagger
    # path('products/popular/', views., name=""),  #GET
    # path('products/limited/', views., name=""),  #GET
    path(
        'product/<int:id>/',
        apis.ProductDetailApi.as_view(),
        name="product-detail"
    ),  #GET
    # path('product/<int:id>/review/', views., name=""),  #POST
    # path('sales/', views., name="sales"),  #GET
    # path('banners/', views., name="banners"),  #GET
    # path('tags/', views., name="tags"),  #GET
    # path('basket/', views., name="basket"),  #GET POST DELETE
    # path('orders/', views., name=""),  #GET POST
    # path('orders/<int:id>/', views., name=""),  #GET POST
]
