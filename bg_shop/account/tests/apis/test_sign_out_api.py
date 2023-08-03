from string import ascii_letters, digits
from random import choices, randint

from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model, get_user

UserModel = get_user_model()


class PostSignOutApiViewTestCase(TestCase):
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

    def test_post_sign_out(self) -> None:
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse("api:account:sign-out"),
        )
        self.assertEqual(response.status_code, 200, "Status code is Not 200.")
        self.assertFalse(
            get_user(self.client).is_authenticated,
            "User is still authenticated.",
        )

    def test_post_sign_out_if_already_out(self) -> None:
        response = self.client.post(
            reverse("api:account:sign-out"),
        )
        self.assertEqual(response.status_code, 200, "Status code is Not 200.")
        self.assertFalse(
            get_user(self.client).is_authenticated,
            "User is still authenticated.",
        )
