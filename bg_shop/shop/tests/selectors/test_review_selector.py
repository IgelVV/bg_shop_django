from django.test import TestCase
from django.contrib.auth import get_user_model

from shop.models import Review
from shop.selectors import ReviewSelector

User = get_user_model()


class GetReviewsForProductTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_review",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ReviewSelector()

    def test_get_reviews_for_product(self):
        product_id = 1
        queryset = self.selector.get_reviews_for_product(product_id)
        expected_result = Review.objects.filter(product=product_id)

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            set(expected_result.values_list("id", flat=True))
        )


class CountReviewsForProductTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_review",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ReviewSelector()

    def test_count_reviews_for_product(self):
        product_id = 1
        count = self.selector.count_reviews_for_product(product_id)
        expected_count = Review.objects.filter(product_id=product_id).count()

        self.assertEqual(count, expected_count)
