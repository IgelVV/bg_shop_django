from django.urls import path

from shop import apis

app_name = "shop"

urlpatterns = [
    path('categories/', apis.CategoryApi.as_view(), name="categories"),  # GET
    path('catalog/', apis.CatalogApi.as_view(), name="catalog"),  # GET sort: rating, price, reviews, date, title
    path(
        'products/popular/',
        apis.ProductPopularApi.as_view(),
        name="products_popular",
    ),  # GET
    path(
        'products/limited/',
        apis.ProductLimitedApi.as_view(),
        name="products_limited"),  # GET
    path(
        'product/<int:id>/',
        apis.ProductDetailApi.as_view(),
        name="product-detail"
    ),  # GET
    path('product/<int:id>/review/', apis.ReviewApi.as_view(), name="review"),  # POST
    path('sales/', apis.SalesApi.as_view(), name="sales"),  # GET
    path('banners/', apis.BannerApi.as_view(), name="banners"),  # GET
    # path('tags/', views., name="tags"),  # GET
]
