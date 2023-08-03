from django.test import TestCase
from shop.selectors import BannerSelector


class GetBanners(TestCase):
    fixtures = [
        "test_product",
        "test_banner",
    ]

    def test_related_products_are_cached(self):
        result = BannerSelector().get_banners()
        self.assertIn('product', result.first()._state.fields_cache)
