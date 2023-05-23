from django.urls import path

from shop import apis

app_name = "shop"

urlpatterns = [
    path('categories/', apis.CategoryApi.as_view(), name="categories"),  #GET
    path('catalog/', apis.CatalogApi.as_view(), name="catalog"),  #GET ${category.id}
    # path('products/popular/', views., name=""),  #GET
    # path('products/limited/', views., name=""),  #GET
    path(
        'product/<int:id>/',
        apis.ProductDetailApi.as_view(),
        name="product-detail"
    ),  #GET
    path('product/<int:id>/review/', apis.ReviewApi.as_view(), name="review"),  #POST
    # path('sales/', views., name="sales"),  #GET
    # path('banners/', views., name="banners"),  #GET
    # path('tags/', views., name="tags"),  #GET
]
