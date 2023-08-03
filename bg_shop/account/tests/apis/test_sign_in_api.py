from string import ascii_letters, digits
from random import choices, randint

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, get_user

UserModel = get_user_model()


class PostLogInApiViewTestCase(TestCase):
    def setUp(self) -> None:
        self.username = "".join(
            choices(ascii_letters+digits, k=randint(1, 10)))
        self.password = "password"
        self.email = "qwerty@dot.com"
        self.user = UserModel.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email,
        )

    def tearDown(self) -> None:
        self.user.delete()

    def test_post_log_in(self) -> None:
        data = {
            "username": self.username,
            "password": self.password,
        }
        response = self.client.post(
            reverse("api:account:sign-in"),
            data=data
        )
        self.assertEqual(response.status_code, 200, "Status code is Not 200.")
        self.assertTrue(
            get_user(self.client).is_authenticated,
            "User is Not authenticated.",
        )

    def test_post_log_in_with_wrong_password(self) -> None:
        data = {
            "username": self.username+"1",
            "password": self.password,
        }
        response = self.client.post(
            reverse("api:account:sign-in"),
            data=data
        )
        self.assertEqual(
            response.status_code,
            403,
            "Wrong status code."
        )

    def test_log_in_inactive_user(self,):
        self.user.is_active = False
        self.user.save()
        data = {
            "username": self.username,
            "password": self.password,
        }
        response = self.client.post(
            reverse("api:account:sign-in"),
            data=data
        )
        self.assertEqual(
            response.status_code,
            403,
            "Wrong status code."
        )
        self.assertFalse(
            get_user(self.client).is_authenticated,
            "User is authenticated despite he is inactive.",
        )
