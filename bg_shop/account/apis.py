from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, permissions
from rest_framework import exceptions as drf_exceptions
from rest_framework import response as drf_response
from rest_framework import request as drf_request
from rest_framework import views
from django.core import exceptions
from django.contrib.auth import password_validation, login, logout

from account import services


User = get_user_model()


class SignInApi(views.APIView):
    """Log in"""
    permission_classes = (permissions.AllowAny,)

    class InputSerializer(serializers.Serializer):
        username = serializers.CharField(max_length=150)
        password = serializers.CharField(max_length=128)

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
    permission_classes = (permissions.AllowAny,)

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(
            max_length=150, required=False, allow_blank=True)
        username = serializers.CharField(max_length=150)
        password = serializers.CharField(max_length=128)

        def validate(self, data):
            """"""
            password = data.get('password')
            errors = dict()
            try:
                password_validation.validate_password(
                    password=password)
            except exceptions.ValidationError as e:
                errors['password'] = list(e.messages)
            if errors:
                raise exceptions.ValidationError(errors)
            return super().validate(data)

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
