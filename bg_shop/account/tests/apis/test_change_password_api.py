from string import ascii_letters, digits
from random import choices, randint

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, get_user

UserModel = get_user_model()


class PostChangePasswordApiViewTestCase(TestCase):
    def setUp(self) -> None:
        self.username = "".join(
            choices(ascii_letters+digits, k=randint(1, 10)))
        self.password = "password"
        self.new_password = "New_password123"
        self.email = "qwerty@dot.com"
        self.user = UserModel.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email,
        )
        self.client.login(username=self.username, password=self.password)

    def tearDown(self) -> None:
        self.user.delete()

    def test_change_password(self):
        data = {
            "password": self.new_password,
        }
        response = self.client.post(
            reverse("api:account:password"),
            data=data
        )
        self.assertEqual(response.status_code, 200, "Wrong status code.")

        self.client.logout()
        self.client.login(username=self.username, password=self.new_password)
        self.assertTrue(
            get_user(self.client).is_authenticated,
            "New password has not been set.",
        )

    def test_if_user_is_not_authenticated(self) -> None:
        self.client.logout()
        data = {
            "password": self.new_password,
        }
        response = self.client.post(
            reverse("api:account:password"),
            data=data
        )
        self.assertEqual(response.status_code, 403, "Wrong status code.")

    def test_set_the_same_password(self):
        data = {
            "password": self.password,
        }
        response = self.client.post(
            reverse("api:account:password"),
            data=data
        )
        self.assertEqual(response.status_code, 400, "Wrong status code.")

    def test_set_too_common_password(self):
        data = {
            "password": "common",
        }
        response = self.client.post(
            reverse("api:account:password"),
            data=data
        )
        self.assertEqual(response.status_code, 400, "Wrong status code.")

