import io
import os
from string import ascii_letters, digits
from random import choices, randint

from PIL import Image

from django.test import TestCase
from django.core.files import File
from django.conf import settings

from common import models, services


def generate_image_file(file_name: str):
    file = io.BytesIO()
    image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
    image.save(file, 'png')
    file.name = file_name
    file.seek(0)
    return file


def generate_image_path(image_name):
    return os.path.join(
        settings.MEDIA_ROOT, settings.IMAGE_SUBDIR, image_name)


def remove_file_from_filesystem(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


class GetImgUrlTestCase(TestCase):
    def test_get_correct_src(self):
        image = models.Image(
            description="test_description",
            img="sesrgas.sf",
        )
        url = services.ImageService().get_img_url(image)
        img_url = image.img.url
        self.assertEqual(url, img_url, "Wrong image URL.")


class DeleteImgTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = services.ImageService()

    def setUp(self) -> None:
        self.base_image_name = "".join(
            choices(ascii_letters + digits, k=randint(9, 10)))
        self.image_name = self.base_image_name + ".png"
        self.image_path = generate_image_path(image_name=self.image_name)

        self.image_file = File(generate_image_file(self.image_name))

    def tearDown(self) -> None:
        remove_file_from_filesystem(self.image_path)
        models.Image.objects.all().delete()

    def test_delete_img_file(self):
        image = models.Image(
            description="test_delete_img_description",
            img=self.image_file,
        )
        image.save()

        self.service.delete_img(instance=image)
        self.assertFalse(
            os.path.exists(self.image_path),
            "Image file steel is in a filesystem.",
        )


class DeleteInstanceTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = services.ImageService()

    def setUp(self) -> None:
        self.base_image_name = "".join(
            choices(ascii_letters + digits, k=randint(9, 10)))
        self.image_name = self.base_image_name + ".png"
        self.image_path = generate_image_path(image_name=self.image_name)

        self.image_file = File(generate_image_file(self.image_name))

    def tearDown(self) -> None:
        remove_file_from_filesystem(self.image_path)
        models.Image.objects.all().delete()

    def test_delete_image_and_related_img_file(self):
        image = models.Image(
            description="test_delete_Image_description",
            img=self.image_file,
        )
        image.save()

        self.service.delete_instance(instance=image)
        self.assertFalse(
            os.path.exists(self.image_path),
            "Image file steel is in a filesystem.",
        )
        self.assertEqual(
            models.Image.objects.count(), 0, "Image object steel exists.")

    def test_delete_unsaved_image(self):
        image = models.Image(
            description="test_delete_Image_description",
            img=self.image_file,
        )
        with self.assertRaises(
                ValueError, msg="Unsaved or deleted Image can't be deleted"):
            self.service.delete_instance(instance=image)


class UpdateInstanceTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = services.ImageService()

    def setUp(self) -> None:
        self.base_image_name = "".join(
            choices(ascii_letters + digits, k=randint(9, 10)))
        self.image_name = self.base_image_name + ".png"
        self.image_path = generate_image_path(image_name=self.image_name)
        self.new_image_name = "new_" + self.image_name
        self.new_image_path = generate_image_path(
            image_name=self.new_image_name)

        self.image_file = File(generate_image_file(self.image_name))
        self.new_image_file = File(generate_image_file(self.new_image_name))

    def tearDown(self) -> None:
        remove_file_from_filesystem(self.image_path)
        remove_file_from_filesystem(self.new_image_path)
        models.Image.objects.all().delete()

    def test_replaced_img_file_is_deleted_from_filesystem(self):
        image = models.Image(
            description="test_delete_Image_description",
            img=self.image_file,
        )
        image.save()
        self.service.update_img(instance=image, new_img=self.new_image_file)
        self.assertFalse(
            os.path.exists(self.image_path),
            "Image file steel is in a filesystem.",
        )
        self.assertTrue(
            os.path.exists(self.new_image_path),
            "New image file is not in a filesystem.",
        )
        self.assertIn(
            self.new_image_name,
            str(image.img),
            "New image file has not been set as img.",
        )

    def test_update_unsaved_image_object(self):
        image = models.Image(
            description="test_delete_Image_description",
            img=self.image_file,
        )
        self.service.update_img(instance=image, new_img=self.new_image_file)
        self.assertTrue(
            os.path.exists(self.new_image_path),
            "New image file is not in a filesystem.",
        )
        self.assertIn(
            self.new_image_name,
            str(image.img),
            "New image file has not been set as img.",
        )
        self.assertTrue(
            models.Image.objects.filter(description=image.description).exists(),
            "Image object has not been saved.")
