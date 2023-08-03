from django.test import TestCase

from common import models, serializers


class GetSrcTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.image = models.Image(
            description="test_description",
            img="path/to/test/image",
        )

    def test_get_correct_src(self):
        serializer = serializers.ImageSerializer(instance=self.image)
        src = serializer.data["src"]
        img_url = self.image.img.url
        self.assertEqual(src, img_url, "`src` key is not equal to img URL.")
