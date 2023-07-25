from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from shop import models
from shop.apis import CategoryApi


class CategoryApiGetTestCase(TestCase):
    fixtures = [
        "test_category",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("api:shop:categories")

    @patch('shop.selectors.CategorySelector.get_root_categories_queryset')
    def test_get(self, mock_get_root_categories_queryset):
        categories = models.Category.objects.filter(parent=None)
        mock_get_root_categories_queryset.return_value = categories

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_root_categories_queryset.assert_called_once_with()
        self.assertListEqual(
            response.data,
            [
                {
                    "id": 1,
                    "title": "test Strategy",
                    "image": None,
                    "subcategories": [
                        {
                            "id": 2,
                            "title": "test AreaMajority",
                            "image": None,
                            "subcategories": [],
                        }
                    ],
                },
                {
                    "id": 3,
                    "title": "Party",
                    "image": None,
                    "subcategories": [],
                },
            ],
        )


class CategoryApiOutputSerializerTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = models.Category.objects.create(title="Category 1")
        subcategories = [
            models.Category.objects.create(
                title="Subcategory 1", parent=cls.category),
            models.Category.objects.create(
                title="Subcategory 2", parent=cls.category),
        ]
        cls.category.category_set.set(subcategories)

    def test_serialize_category(self):
        serializer = CategoryApi.OutputSerializer(self.category)
        data = serializer.data
        expected_data = {
            "id": 1,
            "title": "Category 1",
            "image": None,
            "subcategories": [
                {
                    "id": 2,
                    "title": "Subcategory 1",
                    "image": None,
                    "subcategories": [],
                },
                {
                    "id": 3,
                    "title": "Subcategory 2",
                    "image": None,
                    "subcategories": [],
                },
            ],
        }

        self.assertEqual(
            data,
            expected_data,
        )

    def test_get_subcategories(self):
        serializer = CategoryApi.OutputSerializer(self.category)
        data = serializer.data

        self.assertListEqual(
            data["subcategories"],
            [
                {
                    "id": 2,
                    "title": "Subcategory 1",
                    "image": None,
                    "subcategories": [],
                },
                {
                    "id": 3,
                    "title": "Subcategory 2",
                    "image": None,
                    "subcategories": [],
                },
            ],
        )
