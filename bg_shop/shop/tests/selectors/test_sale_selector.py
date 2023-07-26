from datetime import datetime
from django.test import TestCase
from unittest.mock import patch

from shop.models import Sale
from shop.selectors import SaleSelector


class GetSalesTestCase(TestCase):
    fixtures = [
        "test_product",
        "test_sale",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = SaleSelector()

    def test_get_sales_only_current_false(self):
        queryset = self.selector.get_sales(only_current=False)
        expected_result = Sale.objects.all()

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            set(expected_result.values_list("id", flat=True))
        )
        self.assertIn("product", queryset[0]._state.fields_cache)
        self.assertIn("images", queryset[0].product._prefetched_objects_cache)

    @patch('django.utils.timezone.now')
    def test_get_sales_only_current(
            self,
            mock_now,
    ):
        mock_now.return_value = datetime(2024, 7, 1)
        queryset = self.selector.get_sales(only_current=True)
        expected_result = Sale.objects.filter(
            date_from__lte=mock_now().date(),
            date_to__gte=mock_now().date()
        )

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            set(expected_result.values_list("id", flat=True))
        )
        self.assertIn("product", queryset[0]._state.fields_cache)
        self.assertIn("images", queryset[0].product._prefetched_objects_cache)
