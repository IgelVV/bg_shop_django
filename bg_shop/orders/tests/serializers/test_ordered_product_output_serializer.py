from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from orders.models import Order, OrderedProduct
from orders.serializers import OrderedProductOutputSerializer
from common.models import Image
from shop.models import Product, Tag, Review

UserModel = get_user_model()


class OrderedProductOutputSerializerTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username='testuser', email='test@example.com')
        self.order = Order.objects.create(
            user=self.user,
            delivery_type=Order.DeliveryTypes.EXPRESS,
            payment_type=Order.PaymentTypes.ONLINE,
            city='Test City',
            address='Test Address',
            comment='Test Comment',
            paid=True,
            status=Order.Statuses.COMPLETED,
        )
        self.product = Product.objects.create(
            price=50,
            count=50,
            release_date=timezone.now().date(),
            title='Test Product',
            description='Test Description',
            manufacturer='test',
        )
        self.image = Image.objects.create(img="/media/test", product=self.product)
        self.product.images.add(self.image)
        Review.objects.create(
            author=self.user,
            product=self.product,
            rate=4,
            text='Great product!',
        )
        Review.objects.create(
            author=self.user,
            product=self.product,
            rate=5,
            text='Excellent!',
        )
        self.ordered_product = OrderedProduct.objects.create(
            order=self.order, product=self.product, count=2, price=40)
        self.tag1 = Tag.objects.create(name='Tag 1')
        self.tag2 = Tag.objects.create(name='Tag 2')
        self.product.tags.add(self.tag1, self.tag2)

    def tearDown(self) -> None:
        self.ordered_product.delete()
        self.product.delete()
        Tag.objects.all().delete()
        Review.objects.filter(author=self.user).delete()
        self.image.delete()
        self.order.delete()
        self.user.delete()



    def test_ordered_product_output_serializer_fields(self):
        serializer = OrderedProductOutputSerializer(
            instance=self.ordered_product)

        expected_data = {
            "id": self.ordered_product.product.pk,
            "category": self.ordered_product.product.category_id,
            "price": '40.00',
            "count": 2,
            "date": self.ordered_product.product.release_date.isoformat(),
            "title": self.ordered_product.product.title,
            "description": self.ordered_product.product.short_description,
            "freeDelivery": True,
            "images": [
                OrderedDict([('src', '/media/media/test'), ('alt', None)]),
            ],
            "tags": [
                OrderedDict([('id', 1), ('name', 'Tag 1')]),
                OrderedDict([('id', 2), ('name', 'Tag 2')])
            ],
            "reviews": 2,
            "rating": 4.5,
        }
        self.assertDictEqual(
            serializer.data, expected_data, "Unexpected data.")

    def test_get_rating(self):
        serializer = OrderedProductOutputSerializer()
        expected_rating = 4.5
        actual_rating = serializer.get_rating(self.ordered_product)
        self.assertEqual(
            actual_rating, expected_rating, "Unexpected average rating.")
