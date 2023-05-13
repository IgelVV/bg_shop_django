from django.urls import path

from account import apis


app_name = "account"

urlpatterns = [
    path('sign-in/', apis.SignInApi.as_view(), name="sign-in"),
    path('sign-up/', apis.SignUpApi.as_view(), name="sign-up"),
    path('sign-out/', apis.SignOutApi.as_view(), name="sign-out"),
    path('profile/', apis.ProfileApi.as_view(), name="profile"),
    path(
        'profile/password/',
        apis.ChangePasswordApi.as_view(),
        name="password"
    ),
    path('profile/avatar/', apis.UpdateAvatarApi.as_view(), name="avatar"),
]
