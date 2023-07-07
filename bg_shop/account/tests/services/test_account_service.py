from django.test import TestCase
from django.contrib.auth import get_user_model

from account import services

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
        cls.email = "email@dot.com"
        cls.first_name = "first_name"
        cls.last_name = "last_name"

        cls.service = services.AccountService()

    def tearDown(self) -> None:
        user = UserModel.objects.filter(username=self.username).first()
        if user is not None:
            user.delete()

    def test_change_password(self):
        ...

    def test_set_the_same_password(self):
        ...

    def test_set_empty_password(self):
        ...


class UpdateAvatarTestCase(TestCase):
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

    def test_set_image(self):
        ...

    def test_set_None(self):
        ...


class GetOrCreateProfileTestCase(TestCase):
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


class UpdateAccountTestCase(TestCase):
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


class LoginTestCase(TestCase):
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
