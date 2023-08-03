from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from shop.apis import TagApi
from shop import models


class TagApiGetTestCase(TestCase):
    fixtures = [
        "test_tag",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("api:shop:tags")

    def test_get_all_tags(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), models.Tag.objects.count())

    @patch("shop.selectors.tag_selectors.TagSelector.get_category_tags")
    def test_get_tags_by_category(
            self,
            mock_get_category_tags,
    ):
        mock_get_category_tags.return_value = models.Tag.objects.all()

        response = self.client.get(self.url, {"category": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), models.Tag.objects.count())
        mock_get_category_tags.assert_called_once_with(category_id=1)


class TagApiOutputSerializerTestCase(TestCase):
    fixtures = [
        "test_tag",
    ]

    def test_output_serializer(self):
        tag = models.Tag.objects.get(pk=1)
        serializer = TagApi.OutputSerializer(tag)
        data = serializer.data
        expected_data = {
            "id": tag.pk,
            "name": tag.name,
        }

        self.assertEqual(data, expected_data)
