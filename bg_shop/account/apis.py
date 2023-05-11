from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, permissions, views
from rest_framework import exceptions as drf_exceptions
from rest_framework import response as drf_response
from rest_framework import request as drf_request
from django.contrib.auth import login, logout

from account import services
from account import serializers as account_serializers

User = get_user_model()


class SignInApi(views.APIView):
    """Log in"""

    class InputSerializer(serializers.Serializer):
        username = serializers.CharField(max_length=150)
        password = serializers.CharField(max_length=128)

    permission_classes = (permissions.AllowAny,)
    serializer_class = InputSerializer  # for render

    def post(self, request: drf_request.Request) -> drf_response.Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = authenticate(
            username=data.get('username'), password=data.get('password'))
        if not user:
            raise drf_exceptions.APIException(
                detail={'username': ['Wrong username or password']},
                code=status.HTTP_401_UNAUTHORIZED
            )
        if user is not None:
            login(request, user)
        return drf_response.Response(status=status.HTTP_200_OK)


class SignUpApi(views.APIView):
    """Creates new user and profile"""

    class InputSerializer(account_serializers.PasswordSerializer):
        name = serializers.CharField(
            max_length=150, required=False, allow_blank=True)
        username = serializers.CharField(max_length=150)

    permission_classes = (permissions.AllowAny,)
    serializer_class = InputSerializer

    def post(self, request: drf_request.Request) -> drf_response.Response:
        """If user is successfully created performs log in."""
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = services.AccountService()
        data = serializer.validated_data
        data['first_name'] = data.pop('name')
        user = service.register_user(**data)
        if not user:
            raise drf_exceptions.APIException(
                detail={'username': ['This user already exists.']},
                code=status.HTTP_409_CONFLICT
            )
        if user is not None:
            login(request, user)
        return drf_response.Response(status=status.HTTP_201_CREATED)


class SignOutApi(views.APIView):
    """Log out"""
    permission_classes = (permissions.AllowAny,)

    def post(self, request: drf_request.Request) -> drf_response.Response:
        logout(request)
        return drf_response.Response(status=status.HTTP_200_OK)


class ChangePasswordApi(views.APIView):
    """Change user password, it is prohibited to set the same password"""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = account_serializers.PasswordSerializer

    def post(self, request: drf_request.Request) -> drf_response.Response:
        serializer = self.serializer_class(data=request.data)
        service = services.AccountService()
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            service.change_password(
                user=request.user, password=data['password'])
        except ValueError as e:
            raise drf_exceptions.APIException({'password': e})

        return drf_response.Response(status=status.HTTP_200_OK)


class UpdateAvatarApi(views.APIView):
    """Set new avatar or change it"""

    class InputSerializer(serializers.Serializer):
        avatar = serializers.ImageField()

    serializer_class = InputSerializer

    def post(self, request: drf_request.Request) -> drf_response.Response:
        serializer = self.InputSerializer(data=request.data)
        service = services.AccountService()
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        service.update_avatar(user=request.user, avatar=data['avatar'])
        return drf_response.Response(status=status.HTTP_201_CREATED)


class ProfileApi(views.APIView):
    class ProfileSerializer(serializers.Serializer):
        fullName = serializers.CharField(max_length=300, allow_blank=True)
        email = serializers.EmailField(allow_blank=True)
        phone = serializers.CharField(max_length=10, allow_blank=True)
        avatar = serializers.ImageField()

    serializer_class = ProfileSerializer

    def get(self, request: drf_request.Request) -> drf_response.Response:
        # selector = selectors.ProfileSelector()
        # account = selector.get_account_data(request.user)
        serializer = self.ProfileSerializer(accaunt)
        return drf_response.Response(data=serializer.data, status=status.HTTP_200_OK)
