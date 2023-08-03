from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status

from shop.apis import ReviewApi
from shop import models

UserModel = get_user_model()


class ReviewApiPostTestCase(TestCase):
    fixtures = [
        "test_product",
        "test_user",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = models.Product.objects.get(pk=1)
        cls.url = reverse("api:shop:review", args=[cls.product.pk])
        cls.user = UserModel.objects.get(pk=1)

    @patch('shop.services.ReviewService.create_review')
    @patch('shop.selectors.ReviewSelector.get_reviews_for_product')
    def test_post_review(
            self,
            mock_get_reviews_for_product,
            mock_create_review,
    ):
        mock_create_review.return_value = None
        mock_get_reviews_for_product.return_value = []

        self.client.force_login(user=self.user)
        response = self.client.post(self.url, {
            'text': 'Great product!',
            'rate': 5,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        mock_create_review.assert_called_once_with(
            user_id=self.user.id,
            product_id=self.product.pk,
            text='Great product!',
            rate=5,
        )
        mock_get_reviews_for_product.assert_called_once_with(
            product_id=self.product.pk,
        )


class ReviewApiInputSerializerTestCase(TestCase):
    def test_valid_data(self):
        data = {
            'text': 'Great product!',
            'rate': 5,
        }
        serializer = ReviewApi.InputSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, data)

    def test_invalid_data(self):
        data = {
            'text': 'This is a very long text' + 1024 * "!",
            'rate': -1,
        }
        serializer = ReviewApi.InputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        expected_errors = {
            'text': ['Ensure this field has no more than 1024 characters.'],
            'rate': ['Ensure this value is greater than or equal to 0.'],
        }
        self.assertEqual(serializer.errors, expected_errors)


class ReviewApiOutputSerializerTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserModel.objects.get(pk=1)
        cls.user.email = "test@email.com"
        cls.user.save()
        cls.review = models.Review.objects.create(
            product=models.Product.objects.get(pk=1),
            author=cls.user,
            text='Great product!',
            rate=5,
        )

    def test_serialize_review(self):
        serializer = ReviewApi.OutputSerializer(self.review)
        data = serializer.data
        expected_data = {
            "author": self.user.username,
            "email": self.user.email,
            "text": "Great product!",
            "rate": 5,
            "date": str(self.review.date.isoformat()).replace('+00:00', 'Z'),
        }
        self.assertEqual(data, expected_data)

    def test_author_email(self):
        serializer = ReviewApi.OutputSerializer(self.review)
        data = serializer.data
        self.assertEqual(data["email"], self.user.email)
