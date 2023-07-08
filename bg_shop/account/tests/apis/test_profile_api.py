from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from account import models
from common import models as common_models

UserModel = get_user_model()


class GetProfileApiTestCase(TestCase):
    def setUp(self) -> None:
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="password",
            email="email@dot.com",
            first_name="first_name",
            last_name="last_name",
        )
        self.avatar = common_models.Image(
            description="avatar_description",
            img="path/to/image"
        )
        self.avatar.save()
        self.profile = models.Profile(
            user=self.user,
            phone_number="0123456789",
            avatar=self.avatar,
        )
        self.profile.save()

        self.client.force_login(self.user)

    def tearDown(self) -> None:
        self.profile.delete()
        self.avatar.delete()
        self.user.delete()

    def test_get_account_info(self):
        response = self.client.get(reverse("api:account:profile"),)
        self.assertContains(
            response, self.user.first_name, msg_prefix="Wrong first_name")
        self.assertContains(
            response, self.user.last_name, msg_prefix="Wrong last_name")
        self.assertContains(
            response, self.user.email, msg_prefix="Wrong email")
        self.assertContains(
            response,
            self.avatar.description,
            msg_prefix="Wrong avatar description",
        )
        self.assertContains(
            response, self.avatar.img, msg_prefix="Wrong avatar image url")
        self.assertContains(
            response, self.profile.phone_number, msg_prefix="Wrong phone")

    def test_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse("api:account:profile"), )
        self.assertEqual(response.status_code, 403, "Wrong status code.", )


class PostProfileApiTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_first_name = "newFirstname"
        cls.new_last_name = "newLastname"
        cls.new_full_name = f"{cls.new_first_name} {cls.new_last_name}"
        cls.new_email = "new@dot.com"
        cls.new_phone = "9876543210"
        cls.new_avatar = {
            "src": "new/path/to/image",
            "alt": "new description",
        }

    def setUp(self) -> None:
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="password",
            email="email@dot.com",
            first_name="first_name",
            last_name="last_name",
        )
        self.avatar = common_models.Image(
            description="avatar_description",
            img="path/to/image"
        )
        self.avatar.save()
        self.profile = models.Profile(
            user=self.user,
            phone_number="0123456789",
            avatar=self.avatar,
        )
        self.profile.save()

        self.client.force_login(self.user)

    def tearDown(self) -> None:
        self.profile.delete()
        self.avatar.delete()
        self.user.delete()

    def test_unauthenticated_user(self):
        self.client.logout()
        data = {
            "fullName": self.new_full_name,
            "email": self.new_email,
            "phone": self.new_phone,
            "avatar": self.new_avatar,
        }
        response = self.client.post(reverse("api:account:profile"), data)
        self.assertEqual(response.status_code, 403, "Wrong status code.", )

    def test_set_new_data(self):
        data = {
            "fullName": self.new_full_name,
            "email": self.new_email,
            "phone": self.new_phone,
            "avatar": self.new_avatar,
        }
        response = self.client.post(
            reverse("api:account:profile"),
            data,
            content_type="application/json")
        self.assertContains(
            response, self.new_first_name, msg_prefix="Wrong new first_name")
        self.assertContains(
            response, self.new_last_name, msg_prefix="Wrong new last_name")
        self.assertContains(
            response, self.new_email, msg_prefix="Wrong new email")
        self.assertContains(
            response, self.new_phone, msg_prefix="Wrong new phone")

        self.assertContains(
            response,
            self.avatar.description,
            msg_prefix="Avatar description has changed",
        )
        self.assertContains(
            response,
            self.avatar.img,
            msg_prefix="Avatar image url has changed",
        )

        user = UserModel.objects.get(pk=self.user.pk)
        self.assertEqual(
            self.new_first_name,
            user.first_name,
            "First name hasn't changed or wrong name has been set."
        )
        self.assertEqual(
            self.new_last_name,
            user.last_name,
            "Last name hasn't changed or wrong last name has been set."
        )

    def test_set_avatar_null(self):
        data = {
            "fullName": self.new_full_name,
            "email": self.new_email,
            "phone": self.new_phone,
            "avatar": None,
        }
        response = self.client.post(
            reverse("api:account:profile"),
            data,
            content_type="application/json")

        self.assertIsNone(
            response.data.get("avatar"),
            "Avatar still in response."
            )
        self.assertFalse(
            common_models.Image.objects.filter(img=self.avatar.img).exists(),
            "Image still exists.",
        )
        self.assertIsNone(
            models.Profile.objects.get(pk=self.profile.pk).avatar,
            "Profile still has avatar.",
        )

    def test_full_name_contains_more_than_two_parts(self):
        data = {
            "fullName": "first second last",
            "email": self.new_email,
            "phone": self.new_phone,
            "avatar": self.new_avatar,
        }
        response = self.client.post(
            reverse("api:account:profile"),
            data,
            content_type="application/json")

        self.assertEqual(response.status_code, 400, "Wrong status code.")

    def test_full_name_contains_less_than_two_parts(self):
        data = {
            "fullName": "only_first",
            "email": self.new_email,
            "phone": self.new_phone,
            "avatar": self.new_avatar,
        }
        response = self.client.post(
            reverse("api:account:profile"),
            data,
            content_type="application/json")
        self.assertEqual(response.status_code, 400, "Wrong status code.")
