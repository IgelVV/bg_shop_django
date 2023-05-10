from django.urls import path

from account import apis

from django.urls import reverse_lazy

app_name = "account"

urlpatterns = [
    # path('sign-in/', views.LoginView.as_view(), name=""), # POST
    path('sign-up/', apis.SignUpApi.as_view(), name="sign-up"), # POST
    # path('sign-out/', views., name=""), # POST
    # path('profile/', views., name="profile"), # GET POST
    # path('profile/password/', views., name=""), # POST
    # path('profile/avatar/', views., name=""), # POST
]

# print(reverse_lazy("account:sign-up"))
