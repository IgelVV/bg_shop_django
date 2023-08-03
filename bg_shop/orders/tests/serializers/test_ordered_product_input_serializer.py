from django.test import TestCase
from orders.serializers import OrderedProductInputSerializer


class OrderedProductInputSerializerTestCase(TestCase):
    def test_ordered_product_input_serializer_fields(self):
        data = {
            "id": 1,
            "category": 2,
            "price": "50.00",
            "count": 2,
            "date": "2023-07-18T12:00:00Z",
            "title": "Test Product",
            "description": "Description of the product",
            "freeDelivery": True,
            "images": [
                {"src": "image_url_1", "alt": "Image 1"},
                {"src": "image_url_2", "alt": "Image 2"},
            ],
            "tags": [
                {"id": 1, "name": "Tag 1"},
                {"id": 2, "name": "Tag 2"},
            ],
            "reviews": 5,
            "rating": "4.75",
        }

        serializer = OrderedProductInputSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        expected_data = {
            "id": 1,
            "category": 2,
            "price": "50.00",
            "count": 2,
            "date": "2023-07-18T12:00:00Z",
            "title": "Test Product",
            "description": "Description of the product",
            "freeDelivery": True,
            "images": [
                {"src": "image_url_1", "alt": "Image 1"},
                {"src": "image_url_2", "alt": "Image 2"},
            ],
            "tags": [
                {"id": 1, "name": "Tag 1"},
                {"id": 2, "name": "Tag 2"},
            ],
            "reviews": 5,
            "rating": "4.75",
        }

        self.assertEqual(serializer.data, expected_data)

    def test_ordered_product_input_serializer_empty_data(self):
        data = {
            "id": 1,
            "count": 2,
            "date": "2023-07-18T12:00:00Z",
        }

        serializer = OrderedProductInputSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        expected_data = {
            "id": 1,
            "category": None,
            "price": "0.00",
            "count": 2,
            "date": "2023-07-18T12:00:00Z",
            "title": None,
            "description": None,
            "freeDelivery": None,
            "images": None,
            "tags": None,
            "reviews": None,
            "rating": None,
        }

        self.assertEqual(serializer.data, expected_data)

    def test_ordered_product_input_serializer_invalid_data(self):
        data = {
            "id": 1,
            "count": "a",
        }
        serializer = OrderedProductInputSerializer(data=data)
        serializer.is_valid()
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "A valid integer is required.", serializer.errors["count"])
        self.assertIn("This field is required.", serializer.errors["date"])
