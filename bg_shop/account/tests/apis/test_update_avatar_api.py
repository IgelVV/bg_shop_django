import io
import os

from string import ascii_letters, digits
from random import choices, randint

from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

UserModel = get_user_model()


class PostUpdateAvatarApiTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = "".join(
            choices(ascii_letters+digits, k=randint(1, 10)))
        cls.password = "password"
        cls.email = "qwerty@dot.com"
        cls.user = UserModel.objects.create_user(
            username=cls.username,
            password=cls.password,
            email=cls.email,
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.login(username=self.username, password=self.password)

        self.base_image_name = "".join(
            choices(ascii_letters+digits, k=randint(9, 10)))
        self.image_name = self.base_image_name + ".png"
        self.image_path = self.generate_image_path(image_name=self.image_name)
        self.new_image_name = "new_" + self.image_name
        self.new_image_path = self.generate_image_path(
            image_name=self.new_image_name)

    def tearDown(self) -> None:
        self.remove_file_from_filesystem(self.image_path)
        self.remove_file_from_filesystem(self.new_image_path)

    @staticmethod
    def generate_image_path(image_name):
        return os.path.join(
            settings.MEDIA_ROOT, settings.IMAGE_SUBDIR, image_name)

    def generate_photo_file(self, file_name: str):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = file_name
        file.seek(0)
        return file

    def remove_file_from_filesystem(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_set_avatar(self):
        photo_file = self.generate_photo_file(self.image_name)

        data = {
            'avatar': photo_file
        }
        response = self.client.post(
            reverse("api:account:avatar"),
            data=data
        )
        self.assertEqual(response.status_code, 201, "Wrong status code.",)

        self.assertContains(
            response=response,
            text=self.base_image_name,
            status_code=201,
            msg_prefix="Filename isn't in response.",
        )
        self.assertContains(
            response=response,
            text=self.username,
            status_code=201,
            msg_prefix="Username isn't in response.",
        )

        expected_src = os.path.join(
            settings.MEDIA_URL,
            settings.IMAGE_SUBDIR,
            self.base_image_name,
        )
        self.assertContains(
            response=response,
            text=expected_src,
            status_code=201,
            msg_prefix="Wrong src URL..",
        )
        self.assertTrue(
            os.path.exists(self.image_path),
            "File not found in filesystem.",
        )

    def test_update_avatar(self):
        first_photo_file = self.generate_photo_file(self.image_name)

        data = {
            'avatar': first_photo_file
        }
        self.client.post(
            reverse("api:account:avatar"),
            data=data
        )

        second_photo_file = self.generate_photo_file(self.new_image_name)
        data = {
            'avatar': second_photo_file
        }
        response = self.client.post(
            reverse("api:account:avatar"),
            data=data
        )
        self.assertEqual(response.status_code, 201, "Wrong status code.", )

    def test_update_with_null(self):
        first_photo_file = self.generate_photo_file(self.image_name)
        data = {
            'avatar': first_photo_file
        }
        self.client.post(
            reverse("api:account:avatar"),
            data=data
        )

        data = {
            'avatar': None
        }
        response = self.client.post(
            reverse("api:account:avatar"),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400, "Wrong status code.",)

    def test_set_avatar_unauthenticated_user(self):
        self.client.logout()
        photo_file = self.generate_photo_file(self.image_name)

        data = {
            'avatar': photo_file
        }
        response = self.client.post(
            reverse("api:account:avatar"),
            data=data
        )
        self.assertEqual(response.status_code, 403, "Wrong status code.", )
