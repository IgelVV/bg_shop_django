import datetime
from decimal import Decimal
from typing import Optional

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import (
    Avg,
    Count,
    Sum,
    QuerySet,
    Subquery,
    OuterRef,
    F,
)
from django.utils import timezone

from shop import models
from shop import filters as shop_filters
from orders import models as order_models
from dynamic_config import selectors as conf_selectors

User = get_user_model()


class ProductSelector:
    def get_active_products(self) -> QuerySet:
        return models.Product.objects.filter(is_active=True)

    def is_available(
            self,
            product: Optional[models.Product] = None,
            product_id: Optional[int] = None,
    ) -> bool:
        """
        Check if product is active and count > 0.

        It possible to pass or product or prodict_id, not both.
        If product is passed, doesn't hit db.
        :param product: Product obj.
        :param product_id: Product.pk.
        :return: bool.
        """
        if (product is not None) and (product_id is not None):
            raise AttributeError("It's prohibited to pass both `product` "
                                 "and `product_id` arguments.")
        if product:
            return product.count > 0 and product.is_active
        elif product_id is not None:
            product = models.Product.objects.get(pk=product_id)
            return product.count > 0 and product.is_active
        else:
            raise AttributeError("None of arguments was passed. "
                                 "It required to pass one of them.")

    def get_rating(self, product_id: int) -> float:
        """
        Returns average rete of all Reviews for this Product.
        :param product_id: id of product
        :return: average rating
        """
        reviews = models.Review.objects \
            .filter(product_id=product_id) \
            .aggregate(Avg("rate"))
        return reviews["rate__avg"]

    def is_free_delivery(self, product: models.Product) -> bool:
        """
        Returns True if product costs more than boundary of free delivery,
        if boundary is not None.
        :param product: item to check
        :return: bool
        """
        boundary = conf_selectors.DynamicConfigSelector() \
            .boundary_of_free_delivery
        if boundary:
            return product.price >= boundary
        else:
            return False

    def get_catalog(
            self,
            *,
            filters: Optional[dict] = None,
            sort_field: Optional[str] = None,
            order: Optional[str] = None,
    ) -> QuerySet[models.Product]:
        """
        Main method to get products for displaying in view.
        :param filters: {'name_of_field': 'value_for_filtering'}
            included annotated
        :param sort_field: name of fields to sort (included annotated)
        :param order: `dec` or `inc` (decrease, increase)
        :return: sorted and filtered query set of Products
        """
        filters = filters or {}
        qs = self.get_active_products()
        qs = self._prefetch_for_product_short_serializer(query_set=qs)
        qs = shop_filters.BaseProductFilter(data=filters, queryset=qs).qs
        if sort_field:
            qs = self._sort_catalog(
                query_set=qs, sort_field=sort_field, order=order)
        return qs

    def _prefetch_for_product_short_serializer(
            self,
            query_set: QuerySet[models.Product],
    ) -> QuerySet[models.Product]:
        """
        Prefetches data for using in serializer
        :param query_set:
        :return:
        """
        query_set = query_set.prefetch_related("review_set") \
            .prefetch_related("images") \
            .prefetch_related("tags") \
            .prefetch_related("sale_set")
        return query_set

    def _sort_catalog(
            self,
            query_set: QuerySet[models.Product],
            sort_field: str,
            order: Optional[str] = None,
    ) -> QuerySet[models.Product]:
        """
        Sorts queryset (qs) of Products.
        :param query_set: qs to sort
        :param sort_field: it can be in list:
            "rating",
            "price",
            "reviews",
            "date",
            "title",
            "popularity"
        :param order: `dec` or `inc` (decrease, increase)
        :return: sorted qs
        """
        match sort_field:
            case "popularity":
                # sales - number of products sold. Subquery
                sales = order_models.OrderedProduct.objects \
                    .filter(product=OuterRef("pk")) \
                    .filter(order__status=order_models.Order.Statuses.COMPLETED) \
                    .values("product") \
                    .annotate(sales=Sum("count")).values("sales")
                query_set = query_set.annotate(popularity=Subquery(sales))
            case 'rating':
                query_set = query_set.annotate(rating=Avg('review__rate'))
            case 'reviews':
                query_set = query_set.annotate(reviews=Count('review'))
            case 'date':
                query_set = query_set.annotate(date=F("release_date"))

        if (order is None) or (order == 'dec'):
            sort_field = "-" + sort_field
        elif order == 'inc':
            pass
        else:
            raise ValueError(f"Argument `order` should be str('inc'), "
                             f"str('dec') or None type, but '{order}' instead")

        query_set = query_set.order_by(sort_field)
        return query_set

    def get_products_in_banners(self) -> QuerySet[models.Product]:
        """
        Returns Products to banner view
        :return: query set of Products, that related to Banners
        """
        qs = models.Product.objects.filter(banner__isnull=False)
        qs = self._prefetch_for_product_short_serializer(query_set=qs)
        return qs

    def get_popular_products(self) -> QuerySet[models.Product]:
        """
        Returns products sorted by number of amount sold, and limited
        by POPULAR_PRODUCTS_LIMIT
        :return: annotated qs
        """
        qs = self.get_catalog(sort_field='popularity')
        qs = qs[:settings.POPULAR_PRODUCTS_LIMIT]
        return qs

    def get_limited_products(self) -> QuerySet[models.Product]:
        """
        Returns products with attribute `limited_edition` = True, and limited
        by LIMITED_PRODUCTS_LIMIT
        :return: annotated qs
        """
        qs = self.get_active_products()
        qs = qs.filter(limited_edition=True)
        qs = self._prefetch_for_product_short_serializer(query_set=qs)
        qs = qs[:settings.LIMITED_PRODUCTS_LIMIT]
        return qs

    def get_discounted_price(
            self,
            product: models.Product,
            date: Optional[datetime.date] = None,
    ) -> Decimal:
        """It is better to prefetch Sale objects related to product.
        Uses active sale with the biggest discount"""
        if date is None:
            date = timezone.now().date()
        sale = product.sale_set.filter(
            date_from__lte=date,
            date_to__gte=date,
        ) \
            .order_by("-discount") \
            .first()
        original_price = Decimal(product.price)
        if sale:
            discounted_price = Decimal(
                1 - sale.discount * 0.01) * original_price
            discounted_price = round(discounted_price, 2)
            return discounted_price
        else:
            return original_price
