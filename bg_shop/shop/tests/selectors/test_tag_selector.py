from django.test import TestCase

from shop.models import Tag
from shop.selectors import TagSelector


class GetCategoryTagsTestCase(TestCase):
    fixtures = [
        "test_catalog",
        "test_category",
        "test_tag",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = TagSelector()
        Tag.objects.create(name="new")

    def test_get_category_tags(self):
        category_id = 1
        queryset = self.selector.get_category_tags(category_id)
        expected_result = Tag.objects.filter(
            product__category=category_id).distinct()

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            set(expected_result.values_list("id", flat=True))
        )


class GetTagsTestCase(TestCase):
    fixtures = [
        "test_tag",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = TagSelector()

    def test_get_tags(self):
        queryset = self.selector.get_tags()
        expected_result = Tag.objects.all()

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            set(expected_result.values_list("id", flat=True))
        )
