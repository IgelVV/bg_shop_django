from string import ascii_letters, digits
from random import choices, randint

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, get_user

UserModel = get_user_model()


class PostSignUpApiViewTestCase(TestCase):
    def setUp(self) -> None:
        self.name = "".join(
            choices(ascii_letters + digits, k=randint(1, 10)))
        self.username = "".join(
            choices(ascii_letters + digits, k=randint(1, 10)))
        self.password = "StrongPassword1234!"
        self.email = self.username + "@dot.com"

    def tearDown(self) -> None:
        new_user = UserModel.objects.filter(username=self.username).first()
        if new_user is not None:
            new_user.delete()

    def test_sign_up_creates_user(self) -> None:
        data = {
            "name": self.name,
            "username": self.username,
            "password": self.password,
        }
        response = self.client.post(
            reverse("api:account:sign-up"),
            data=data
        )
        self.assertEqual(response.status_code, 201, "Wrong status code.")
        self.assertTrue(
            UserModel.objects.filter(username=self.username).exists(),
            "New user has not been created.",
        )
        self.assertTrue(
            get_user(self.client).is_authenticated,
            "User is Not authenticated.",
        )

    def test_only_username_and_password_without_other_fields(self):
        data = {
            "username": self.username,
            "password": self.password,
        }
        response = self.client.post(
            reverse("api:account:sign-up"),
            data=data
        )
        self.assertEqual(response.status_code, 201, "Wrong status code.")
        self.assertTrue(
            UserModel.objects.filter(username=self.username).exists(),
            "New user has not been created.",
        )
        self.assertTrue(
            get_user(self.client).is_authenticated,
            "User is Not authenticated.",
        )

    def test_sign_up_with_too_common_password(self):
        data = {
            "name": self.name,
            "username": self.username,
            "password": "password",
        }
        response = self.client.post(
            reverse("api:account:sign-up"),
            data=data
        )
        self.assertEqual(response.status_code, 400, "Wrong status code.")
        self.assertFalse(
            UserModel.objects.filter(username=self.username).exists(),
            "New user has been created.",
        )

    def test_sign_up_with_not_ascii_username(self):
        data = {
            "name": self.name,
            "username": "网络",
            "password": self.password,
        }
        response = self.client.post(
            reverse("api:account:sign-up"),
            data=data
        )
        self.assertEqual(response.status_code, 400, "Wrong status code.")
        self.assertFalse(
            UserModel.objects.filter(username=self.username).exists(),
            "New user has been created.",
        )

    def test_user_already_exists(self):
        self.user = UserModel.objects.create_user(
            username=self.username,
            password=self.password,
        )
        data = {
            "name": self.name,
            "username": self.username,
            "password": self.password,
        }
        response = self.client.post(
            reverse("api:account:sign-up"),
            data=data
        )
        self.assertEqual(response.status_code, 409, "Wrong status code.")
