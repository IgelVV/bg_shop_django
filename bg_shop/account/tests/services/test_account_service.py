import io
import os

from string import ascii_letters, digits
from random import choices, randint

from PIL import Image

from django.test import TestCase
from django.core.files import File
from django.core import exceptions
from django.contrib.auth import get_user_model, authenticate
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings

from rest_framework.test import APIRequestFactory

from account import services, models
from common import models as common_models
from shop import models as shop_models

UserModel = get_user_model()


class RegisterUserTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = "testUser"
        cls.password = "password"
        cls.email = "email@dot.com"
        cls.first_name = "first_name"
        cls.last_name = "last_name"

        cls.service = services.AccountService()

    def tearDown(self) -> None:
        user = UserModel.objects.filter(username=self.username).first()
        if user is not None:
            user.delete()

    def test_create_new_user_with_new_profile(self):
        user = self.service.register_user(
            username=self.username,
            password=self.password,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
        )
        self.assertIsNotNone(user, "User hasn't been created")
        self.assertIsNotNone(user.password, "User doesn't have password")
        self.assertNotEquals(
            user.password, self.password, "Password hasn't been encrypted.")

    def test_register_user_with_existed_username(self):
        UserModel.objects.create_user(
            username=self.username,
            password=self.password + "123",
        )
        user = self.service.register_user(
            username=self.username,
            password=self.password,
        )
        self.assertIsNone(user, "User has been created")

    def test_unexpected_extra_fields(self):
        with self.assertRaises(
                TypeError, msg="Unexpected argument has been accepted"):
            self.service.register_user(
                username=self.username,
                password=self.password,
                unexpected_field="some data",
            )


class ChangePasswordTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = "testUser"
        cls.password = "password"
        cls.new_password = "new_password"
        cls.email = "email@dot.com"

        cls.service = services.AccountService()

    def setUp(self) -> None:
        self.user = UserModel.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email,
        )

    def tearDown(self) -> None:
        self.user.delete()

    def test_change_password(self):
        self.service.change_password(self.user, self.new_password)
        user = authenticate(username=self.username, password=self.new_password)
        self.assertIsNotNone(user, "New password isn't set.")

    def test_set_the_same_password(self):
        with self.assertRaises(
                ValueError, msg="The same password doesn't rising exception."):
            self.service.change_password(self.user, self.password)

    def test_set_empty_password(self):
        self.service.change_password(self.user, password="")
        user = authenticate(username=self.username, password="")
        self.assertIsNotNone(user, "Empty password isn't set.")


class UpdateAvatarTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserModel.objects.create_user(
            username="user1",
            password="password",
            email="qwerty@dot.com",
        )
        cls.service = services.AccountService()

    def setUp(self) -> None:
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
        image_file = File(self.generate_photo_file(self.image_name))
        self.service.update_avatar(self.user, image_file)
        self.assertTrue(
            os.path.exists(self.image_path),
            "File not found in filesystem.",
        )
        avatar = self.user.profile.avatar
        self.assertIsNotNone(
            avatar, "Image object hasn't been bind to the profile.")

    def test_update_avatar(self):
        if hasattr(self.user, "profile"):
            profile = self.user.profile
        else:
            profile = models.Profile(user=self.user)

        image_file = File(self.generate_photo_file(self.image_name))
        avatar = common_models.Image(img=image_file, description="description")
        avatar.save()
        profile.avatar = avatar
        profile.save()

        second_image_file = File(self.generate_photo_file(self.new_image_name))
        self.service.update_avatar(self.user, second_image_file)
        new_avatar = self.user.profile.avatar
        self.assertTrue(
            os.path.exists(self.new_image_path),
            "New file not found in filesystem.",
        )
        self.assertIsNotNone(
            new_avatar, "New Image object hasn't been bind to the profile.")
        self.assertFalse(
            common_models.Image.objects.filter(pk=avatar.pk).exists(),
            "Previous Image object hasn't been deleted."
        )

    def test_set_None(self):
        with self.assertRaises(
                exceptions.ValidationError,
                msg="It is possible to pass None"
        ):
            self.service.update_avatar(self.user, None)


class GetOrCreateProfileTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = services.AccountService()

    def setUp(self) -> None:
        self.user = UserModel.objects.create_user(
            username="user1",
            password="password",
            email="qwerty@dot.com",
        )

    def tearDown(self) -> None:
        self.user.delete()

    def test_get_existing_profile_related_to_user(self):
        existing_profile = models.Profile(user=self.user)
        existing_profile.save()
        profile = self.service.get_or_create_profile(user=self.user)
        self.assertEqual(
            existing_profile, profile, "Existing profile hasn't received.")

    def test_create_profile_if_no_related_ones(self):
        profile = self.service.get_or_create_profile(user=self.user)
        self.assertEqual(
            self.user, profile.user, "New Profile isn't related to the User.")

    def test_not_save_if_commit_false(self):
        profile = self.service.get_or_create_profile(
            user=self.user, commit=False)
        self.assertIsNone(
            profile.pk, "New Profile has benn saved, when commit=False.")


class UpdateAccountTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_first_name = "newFirstname"
        cls.new_last_name = "newLastname"
        cls.new_email = "new@dot.com"
        cls.new_phone = "9876543210"
        cls.new_avatar = {
            "src": "new/path/to/image",
            "alt": "new description",
        }
        cls.service = services.AccountService()

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

    def tearDown(self) -> None:
        self.profile.delete()
        if self.avatar.pk:
            self.avatar.delete()
        self.user.delete()

    def test_update_data(self):
        self.service.update_account(
            user=self.user,
            first_name=self.new_first_name,
            last_name=self.new_last_name,
            email=self.new_email,
            phone=self.new_phone,
            avatar=self.new_avatar,
        )
        user = UserModel.objects.get(pk=self.user.pk)
        self.assertEqual(
            user.email, self.new_email, "Wrong email.")
        self.assertEqual(
            user.first_name, self.new_first_name, "Wrong first_name.")
        self.assertEqual(
            user.last_name, self.new_last_name, "Wrong last_name.")
        self.assertEqual(
            user.profile.phone_number, self.new_phone, "Wrong phone_number.")
        self.assertEqual(
            user.profile.avatar, self.avatar, "Avatar has been changed.")

    def test_create_profile_if_not_exists(self):
        user = UserModel.objects.create_user(
            username="testUserWithoutProfile",
            password="password",
        )
        self.service.update_account(
            user=user,
            first_name=self.new_first_name,
            last_name=self.new_last_name,
            email=self.new_email,
            phone=self.new_phone,
            avatar=self.new_avatar,
        )
        self.assertIsNotNone(
            models.Profile.objects.filter(user=user).exists(),
            "Related profile doesn't exists."
        )

    def test_delete_avatar_if_passed_None(self):
        self.service.update_account(
            user=self.user,
            first_name=self.new_first_name,
            last_name=self.new_last_name,
            email=self.new_email,
            phone=self.new_phone,
            avatar=None,
        )
        self.assertFalse(
            common_models.Image.objects.filter(pk=self.avatar.pk).exists(),
            "Avatar Image object hasn't been deleted."
        )

    def test_invalid_email(self):
        with self.assertRaises(
                exceptions.ValidationError,
                msg="Invalid email is accepted.",
        ) as context:

            self.service.update_account(
                user=self.user,
                first_name=self.new_first_name,
                last_name=self.new_last_name,
                email="invalidEmail",
                phone=self.new_phone,
                avatar=self.new_avatar,
            )
        exception = context.exception
        self.assertIn("email", exception.message_dict.keys())

    def test_invalid_phone(self):
        with self.assertRaises(
                exceptions.ValidationError,
                msg="Invalid email is accepted.",
        ) as context:
            self.service.update_account(
                user=self.user,
                first_name=self.new_first_name,
                last_name=self.new_last_name,
                email=self.new_email,
                phone="InvalidPhone",
                avatar=self.new_avatar,
            )
        exception = context.exception
        self.assertIn("phone_number", exception.message_dict.keys())


class LoginTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = services.AccountService()
        cls.username = "testUser"
        cls.password = "password"
        cls.user = UserModel.objects.create_user(
            username=cls.username,
            password=cls.password,
        )

    def setUp(self) -> None:
        self.request = APIRequestFactory().post(
            path='/',
            data={
                'username': self.username,
                'password': self.password,
            },
        )
        # add user attr to request,
        # to allow login() to bind self.user to request
        self.request.user = None

        # create session
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_login(self):
        self.service.login(
            request=self.request,
            user=self.user,
        )
        self.assertEqual(
            self.request.user, self.user, "User is not linked to request")
        self.assertTrue(
            self.request.user.is_authenticated,
            "User is Not authenticated.",
        )

    def test_merge_carts(self):
        product = shop_models.Product(
            title="testProd",
            description="testDescription",
            release_date='2023-01-01',
            manufacturer='test',
            count=100,
        )
        product.save()

        # add cart to session
        cart = self.request.session[settings.CART_SESSION_ID] = {}
        cart[product.pk] = 1
        self.request.session.modified = True

        self.service.login(
            request=self.request,
            user=self.user,
        )
        order_cart = self.user.order_set.first()
        self.assertIsNotNone(
            order_cart, "Cart hasn't been created from session.",)
