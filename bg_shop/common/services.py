"""Services for managing common app."""

from django.db import transaction
from django.core.files import File

from common import models


class ImageService:
    @staticmethod
    def get_img_url(image: models.Image) -> str:
        """
        Gets image url. img field is required.

        :param image: Image obj with img field
        :return: media url
        """
        url: str = image.img.url
        return url

    def delete_img(self, instance: models.Image) -> None:
        """
        Delete img file from filesystem.

        :param instance: Image obj.
        :return: None
        """
        if instance.pk is not None:
            instance.img.delete(save=False)

    def delete_instance(self, instance: models.Image) -> None:
        """
        Delete Image obj.

        To use instead of model.delete() + signals.
        It triggers cleaning up related files.
        :param instance: Image obj.
        :return: None
        """
        with transaction.atomic():
            self.delete_img(instance)
            instance.delete()

    def update_img(self, instance: models.Image, new_img: File) -> None:
        """
        Set new file as image in img field.

        :param instance: Image obj.
        :param new_img: new image file to set in ImageField 'img'.
        :return: None.
        """
        self.delete_img(instance)
        instance.img = new_img
        instance.full_clean()
        instance.save()

