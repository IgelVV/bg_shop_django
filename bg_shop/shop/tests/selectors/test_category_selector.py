from django.test import TestCase
from shop.models import Category
from shop.selectors import CategorySelector


class GetRootCategoriesTestCase(TestCase):
    fixtures = [
        "test_category",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = CategorySelector()

    def test_get_root_categories_queryset(self):
        queryset = self.selector.get_root_categories_queryset(only_active=True)

        expected_result = Category.objects.filter(
            is_active=True,
            parent=None,
        )

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            set(expected_result.values_list("id", flat=True))
        )

        for category in queryset:
            self.assertIsNone(category.parent)
            self.assertTrue(category.is_active)

    def test_related_data_cached(self):
        result = self.selector.get_root_categories_queryset(only_active=True)

        self.assertIn('image', result.first()._state.fields_cache)
        self.assertIn('parent', result.first()._state.fields_cache)


class GetSubcategoriesTestCase(TestCase):
    fixtures = [
        "test_category",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = CategorySelector()

    def test_get_subcategories(self):
        selector = CategorySelector()
        category_id = 1
        queryset = selector.get_subcategories(category_id, only_active=True)
        expected_result = Category.objects.filter(
            parent=category_id, is_active=True)

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            set(expected_result.values_list("id", flat=True))
        )

        for category in queryset:
            self.assertEqual(category.parent_id, category_id)
            self.assertTrue(category.is_active)


class GetAllDescendantsTestCase(TestCase):
    fixtures = [
        "test_category",
    ]

    def test_get_all_descendants(self):
        selector = CategorySelector()
        category_id = 1
        Category.objects.create(
            title="qwerty1u2",
            parent_id=1,
        )
        descendants = selector.get_all_descendants(
            category_id, only_active=True)

        expected_descendants_ids = [2, 4]
        self.assertEqual(len(descendants), len(expected_descendants_ids))

        for descendant in descendants:
            self.assertTrue(descendant.is_active)
            self.assertIn(descendant.pk, expected_descendants_ids)
