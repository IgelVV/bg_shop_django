from django.test import TestCase
from unittest.mock import patch, PropertyMock
from shop.models import Product
from shop.filters import BaseProductFilter


class BaseProductFilterTestCase(TestCase):
    fixtures = [
        "test_tag",
        "test_product",
    ]

    @patch(
        "dynamic_config.selectors.DynamicConfigSelector"
        ".boundary_of_free_delivery",
        new_callable=PropertyMock,
    )
    def test_filter_free_delivery_with_boundary(
            self,
            mock_boundary_of_free_delivery,
    ):
        mock_boundary_of_free_delivery.return_value = 100

        qs = Product.objects.all()
        filter_instance = BaseProductFilter(
            data={"freeDelivery": True}, queryset=qs
        )
        filtered_qs = filter_instance.qs

        self.assertTrue(mock_boundary_of_free_delivery.called)
        self.assertTrue(all(product.price >= 100 for product in filtered_qs))

    @patch(
        "dynamic_config.selectors.DynamicConfigSelector"
        ".boundary_of_free_delivery",
        new_callable=PropertyMock,
    )
    def test_filter_free_delivery_without_boundary(
            self,
            mock_boundary_of_free_delivery
    ):
        mock_boundary_of_free_delivery.return_value = None

        qs = Product.objects.all()
        filter_instance = BaseProductFilter(
            data={"freeDelivery": True}, queryset=qs
        )
        filtered_qs = filter_instance.qs

        self.assertTrue(mock_boundary_of_free_delivery.called)
        self.assertTrue(all(p.freeDelivery is False for p in filtered_qs))
        self.assertEqual(len(filtered_qs), 0)

    def test_filter_available_in_stock(self):
        qs = Product.objects.all()
        filter_instance = BaseProductFilter(
            data={"available": True}, queryset=qs
        )
        filtered_qs = filter_instance.qs

        expected_qs = Product.objects.filter(
            count__gt=0,
            is_active=True,
        )

        self.assertTrue(all(p.count > 0 for p in filtered_qs))
        self.assertTrue(all(p.is_active is True for p in filtered_qs))
        self.assertEqual(
            set(filtered_qs.values_list("id", flat=True)),
            set(expected_qs.values_list("id", flat=True))
        )

    def test_filter_tags(self):
        tag_ids = [1, 2]
        Product.objects.get(pk=1).tags.add(1)
        Product.objects.get(pk=2).tags.add(2)
        Product.objects.get(pk=3).tags.add(1, 2)
        qs = Product.objects.all()
        filter_instance = BaseProductFilter(
            data={"tags": tag_ids}, queryset=qs
        )
        filtered_qs = filter_instance.qs

        expected_qs = Product.objects.filter(
            tags__in=tag_ids,
        ).distinct()
        self.assertEqual(
            set(filtered_qs.values_list("id", flat=True)),
            set(expected_qs.values_list("id", flat=True))
        )
