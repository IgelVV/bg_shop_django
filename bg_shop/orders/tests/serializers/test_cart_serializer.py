from collections import OrderedDict
from decimal import Decimal
from datetime import date

from django.test import TestCase, override_settings
from django.utils import timezone

from shop.models import Product, Category, Review, Sale
from orders.serializers import CartSerializer
from common.models import Image
from dynamic_config.services import DynamicConfigService


@override_settings(BOUNDARY_OF_FREE_DELIVERY=10)
class CartSerializerTestCase(TestCase):
    fixtures = [
        "test_user"
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        DynamicConfigService.set_default_config()

    def setUp(self):
        category = Category.objects.create(title='Test Category')
        self.image = Image.objects.create(img="/media/test")
        self.product = Product.objects.create(
            category=category,
            price=100,
            count=50,
            release_date=timezone.now().date(),
            title='Test Product',
            description='Test Description',
            manufacturer='test',
        )
        self.product.images.add(self.image)
        self.product.quantity_ordered = 3
        Review.objects.create(
            author_id=1,
            product=self.product,
            rate=4,
            text='Great product!',
        )
        Review.objects.create(
            author_id=1,
            product=self.product,
            rate=5,
            text='Excellent!',
        )
        Sale.objects.create(
            product=self.product,
            discount=10,
            date_from=timezone.now().date(),
            date_to=timezone.now().date() + timezone.timedelta(10),
        )

    def test_cart_serializer_fields(self):
        serializer = CartSerializer(instance=self.product)

        expected_data = {
            'id': self.product.id,
            'category': self.product.category_id,
            'price': Decimal(90),
            'count': 3,
            'date': date.today().__str__(),
            'title': 'Test Product',
            'description': 'Test Description...',
            'freeDelivery': True,
            'images': [
                OrderedDict(
                    src='/media/media/test',
                    alt=None,
                ),
            ],
            'tags': [],
            'reviews': 2,
            'rating': 4.5,
        }
        self.assertEqual(
            serializer.data,
            expected_data,
            "Unexpected data."
        )

    def test_get_price(self):
        serializer = CartSerializer()
        # Assuming the discount
        expected_discounted_price = Decimal('90')
        actual_discounted_price = serializer.get_price(self.product)

        self.assertEqual(
            actual_discounted_price,
            expected_discounted_price,
            "Wrong price."
        )

    def test_get_count(self):
        serializer = CartSerializer()
        expected_count = self.product.quantity_ordered
        actual_count = serializer.get_count(self.product)

        self.assertEqual(actual_count, expected_count, "Unexpected count")

    def test_get_freeDelivery(self):
        serializer = CartSerializer()

        self.product.price = Decimal('9')
        expected_free_delivery = False
        actual_free_delivery = serializer.get_freeDelivery(self.product)

        self.assertEqual(
            actual_free_delivery,
            expected_free_delivery,
            "Wrong calculating of free delivery."
        )

    def test_get_reviews(self):
        serializer = CartSerializer()
        expected_reviews = 2
        actual_reviews = serializer.get_reviews(self.product)

        self.assertEqual(
            actual_reviews, expected_reviews, "Unexpected quantity of reviews")

    def test_get_rating(self):
        serializer = CartSerializer()
        expected_rating = 4.5
        actual_rating = serializer.get_rating(self.product)

        self.assertEqual(
            actual_rating, expected_rating, "Unexpected average rating.")
