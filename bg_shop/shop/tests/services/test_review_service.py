from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from shop.models import Review
from shop.services import ReviewService


class CreateReviewTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = ReviewService()

    def test_create_review_with_valid_data(self):
        user_id = 1
        product_id = 2
        text = "This is a test review"
        rate = 4
        date = timezone.now()

        review = self.service.create_review(
            user_id=user_id,
            product_id=product_id,
            text=text,
            rate=rate,
            date=date
        )

        self.assertIsInstance(review, Review)
        self.assertEqual(review.author_id, user_id)
        self.assertEqual(review.product_id, product_id)
        self.assertEqual(review.text, text)
        self.assertEqual(review.rate, rate)
        self.assertEqual(review.date, date)

    def test_create_review_with_default_date(self):
        user_id = 1
        product_id = 2
        text = "This is another test review"
        rate = 5

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = timezone.datetime(
                2023, 1, 1, tzinfo=timezone.utc)

            review = self.service.create_review(
                user_id=user_id,
                product_id=product_id,
                text=text,
                rate=rate
            )

        self.assertIsInstance(review, Review)
        self.assertEqual(review.author_id, user_id)
        self.assertEqual(review.product_id, product_id)
        self.assertEqual(review.text, text)
        self.assertEqual(review.rate, rate)
        self.assertEqual(
            review.date,
            timezone.datetime(2023, 1, 1, tzinfo=timezone.utc),
        )

    def test_create_review_with_commit_false(self):
        user_id = 1
        product_id = 2
        text = "This is a test review"
        rate = 4
        date = timezone.now().date()
        review = self.service.create_review(
            user_id=user_id,
            product_id=product_id,
            text=text,
            rate=rate,
            date=date,
            commit=False
        )

        self.assertIsInstance(review, Review)
        self.assertEqual(review.author_id, user_id)
        self.assertEqual(review.product_id, product_id)
        self.assertEqual(review.text, text)
        self.assertEqual(review.rate, rate)
        self.assertEqual(review.date, date)
        self.assertFalse(review.pk)

        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(author_id=user_id, product_id=product_id)

