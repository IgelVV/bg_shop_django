from django.test import TestCase
from django.contrib.auth import get_user_model

from account import models, selectors
from common import models as common_models

UserModel = get_user_model()


class GetAccountDataTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserModel.objects.create_user(
            username="testUser",
            password="password",
            email="email@dot.com",
            first_name="first_name",
            last_name="last_name",
        )
        cls.avatar = common_models.Image(
            description="avatar_description",
            img="path/to/image"
        )
        cls.avatar.save()
        cls.profile = models.Profile(
            user=cls.user,
            phone_number="0123456789",
            avatar=cls.avatar,
        )
        cls.profile.save()

        cls.selector = selectors.AccountSelector()

    def test_data_is_correct(self):
        data = self.selector.get_account_data(user=self.user)
        expected_data = {
            'fullName': self.user.get_full_name(),
            'email': self.user.email,
            'phone': self.profile.phone_number,
            'avatar': {
                'src': self.avatar.img.url,
                'alt': self.avatar.description,
            }
        }
        self.assertEqual(data, expected_data, "Data is incorrect.")

    def test_user_without_profile(self):
        new_user = UserModel.objects.create_user(
            username="testUser2",
            password="password2",
            email="email2@dot.com",
            first_name="first_name2",
            last_name="last_name2",
        )
        data = self.selector.get_account_data(user=new_user)
        expected_data = {
            'fullName': new_user.get_full_name(),
            'email': new_user.email,
            'phone': "",
            'avatar': None,
        }
        self.assertEqual(data, expected_data, "Data is incorrect.")


class GetAvatarDataTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserModel.objects.create_user(
            username="testUser",
            password="password",
            email="email@dot.com",
            first_name="first_name",
            last_name="last_name",
        )

        cls.selector = selectors.AccountSelector()

    def tearDown(self) -> None:
        if (profile := self.user.profile) is not None:
            if ((avatar := profile.avatar) is not None) \
                    and (avatar.pk is not None):
                avatar.delete()
            profile.delete()

    def test_data_is_correct(self):
        avatar = common_models.Image(
            description="avatar_description",
            img="path/to/image"
        )
        avatar.save()
        profile = models.Profile(
            user=self.user,
            phone_number="0123456789",
            avatar=avatar,
        )
        profile.save()

        data = self.selector.get_avatar_data(profile)
        expected_data = {
            'src': avatar.img.url,
            'alt': avatar.description
        }
        self.assertEqual(data, expected_data, "Data is incorrect.")

    def test_profile_does_not_have_avatar(self):
        profile = models.Profile(
            user=self.user,
            phone_number="0123456789",
        )
        profile.save()
        data = self.selector.get_avatar_data(profile)
        self.assertIsNone(
            data, "None is expected, because profile doesn't have avatar.")

    def test_profile_has_link_to_deleted_avatar(self):
        avatar = common_models.Image(
            description="avatar_description",
            img="path/to/image",
        )
        avatar.save()
        profile = models.Profile(
            user=self.user,
            phone_number="0123456789",
            avatar=avatar,
        )
        profile.save()
        avatar.delete()
        data = self.selector.get_avatar_data(profile)
        self.assertIsNone(
            data,
            "None is expected, because profile has link to deleted avatar.",
        )


