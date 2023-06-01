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
