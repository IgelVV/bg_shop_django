from typing import Any

from django.contrib.auth import get_user_model, authenticate, logout
from django.core import exceptions as django_exceptions

from rest_framework import serializers, status, permissions, views
from rest_framework import exceptions as drf_exceptions
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from account import selectors, services, utils
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
        """
        Logs user in using request credentials
        :param request: DRF request
        :return: DRF response
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = authenticate(
            username=data.get('username'), password=data.get('password'))
        if user is None:
            raise drf_exceptions.APIException(
                detail={'username': ['Wrong username or password']},
                code=status.HTTP_401_UNAUTHORIZED
            )
        else:
            services.AccountService().login(request, user)
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
        """
        If user is successfully created performs log in.
        :param request: DRF request
        :return: DRF response
        :exception APIException: if user already exists
        """
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
            service.login(request, user)
        return drf_response.Response(status=status.HTTP_201_CREATED)


class SignOutApi(views.APIView):
    """Log out"""
    permission_classes = (permissions.AllowAny,)

    def post(self, request: drf_request.Request) -> drf_response.Response:
        """
        Performs logging out. If the user has not been logged in,
        it does nothing and returns 200.
        :param request: DRF request
        :return: DRF response
        """
        logout(request)
        return drf_response.Response(status=status.HTTP_200_OK)


class ChangePasswordApi(views.APIView):
    """Change user password, it is prohibited to set the same password"""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = account_serializers.PasswordSerializer

    def post(self, request: drf_request.Request) -> drf_response.Response:
        """
        Change user password, validates password before sending to service.
        :param request: DRF request
        :return: DRF response
        """
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

    class OutputSerializer(serializers.Serializer):
        src = serializers.CharField()
        alt = serializers.CharField()

    class InputSerializer(serializers.Serializer):
        avatar = serializers.ImageField()

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InputSerializer

    def post(self, request: drf_request.Request) -> drf_response.Response:
        """
        First, creates new Image and relates to current user.
        Second, gets data about new avatar to send back.
        :param request: DRF request
        :return: DRF response
        """
        service = services.AccountService()
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        service.update_avatar(user=request.user, avatar=data['avatar'])

        selector = selectors.AccountSelector()
        profile = service.get_or_create_profile(request.user)
        output_serializer = self.OutputSerializer(
            data=selector.get_avatar_data(profile))
        output_serializer.is_valid()
        return drf_response.Response(
            data=output_serializer.validated_data,
            status=status.HTTP_201_CREATED
        )


class ProfileApi(views.APIView):
    """Provides data about User and related Profile (and Image),
    allows change it"""
    class OutputSerializer(serializers.Serializer):
        class AvatarSerializer(serializers.Serializer):  # todo import from common
            src = serializers.CharField()
            alt = serializers.CharField(max_length=255)

        fullName = serializers.CharField(max_length=300, allow_blank=True)
        email = serializers.EmailField(allow_blank=True)
        phone = serializers.CharField(max_length=10, allow_blank=True)
        avatar = AvatarSerializer(allow_null=True, required=False)

    class InputSerializer(serializers.Serializer):
        # `If you need a nested serializer,use the inline_serializer util.`
        class AvatarSerializer(serializers.Serializer):
            src = serializers.CharField()
            alt = serializers.CharField(max_length=255)

        fullName = serializers.CharField(max_length=300, allow_blank=True)
        email = serializers.EmailField(allow_blank=True)
        phone = serializers.CharField(max_length=10, allow_blank=True)
        avatar = AvatarSerializer(allow_null=True)

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InputSerializer

    def get(self, request: drf_request.Request) -> drf_response.Response:
        """
        Provides data about User and related Profile (and Image).
        :param request: DRF request
        :return: DRF response
        """
        selector = selectors.AccountSelector()
        data: dict[str, Any] = selector.get_account_data(request.user)
        serializer = self.OutputSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return drf_response.Response(
            data=serializer.validated_data, status=status.HTTP_200_OK)

    def post(self, request: drf_request.Request) -> drf_response.Response:
        """
        Changes User and Profile. Splits fullName to put it in the
        database separately.
        :param request: DRF request
        :return: DRF response
        """
        service = services.AccountService()
        selector = selectors.AccountSelector()
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        full_name = serializer.validated_data["fullName"]
        try:
            first_name, last_name = utils.split_full_name(full_name)
        except ValueError as e:
            raise drf_exceptions.ValidationError(e)
        serializer.validated_data['first_name'] = first_name
        serializer.validated_data['last_name'] = last_name
        try:
            service.update_account(
                user=request.user, **serializer.validated_data)
        except django_exceptions.ValidationError as e:
            raise drf_exceptions.ValidationError(e)
        data: dict[str, Any] = selector.get_account_data(user=request.user)
        return drf_response.Response(
            data=data, status=status.HTTP_200_OK)