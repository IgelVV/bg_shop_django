from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import (
    Avg,
    Count,
    Sum,
    QuerySet,
    Subquery,
    OuterRef,
    Case,
    When,
    Value,
    F,
    BooleanField,
)

from shop import models
from shop import filters as shop_filters
from orders import models as order_models
from dynamic_config import selectors as conf_selectors

User = get_user_model()

POPULAR_PRODUCTS_LIMIT = 8  # todo remove to settings (or conf)
LIMITED_PRODUCTS_LIMIT = 6


class ProductSelector:
    def get_active_products(self) -> QuerySet:
        return models.Product.objects.filter(is_active=True)

    def get_rating(self, product_id: int) -> float:
        """
        Returns average rete of all Reviews for this Product.
        :param product_id: id of product
        :return: average rating
        """
        reviews = models.Review.objects\
            .filter(product_id=product_id)\
            .aggregate(Avg("rate"))
        return reviews["rate__avg"]

    def is_free_delivery(self, product: models.Product) -> bool:
        """
        Returns True if product costs more than boundary of free delivery,
        if boundary is not None.
        :param product: item to check
        :return: bool
        """
        boundary = conf_selectors.AdminConfigSelector()\
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
        qs = self._annotate_for_product_short_view(query_set=qs)
        qs = shop_filters.BaseProductFilter(data=filters, queryset=qs).qs
        if sort_field:
            qs = self._sort_catalog(
                query_set=qs, sort_field=sort_field, order=order)
        return qs

    def _annotate_for_product_short_view(
            self,
            query_set: QuerySet[models.Product],
    ) -> QuerySet[models.Product]:
        """
        Annotates query set of Products to simplify serializing and filtering.
        Adds following fields:
            rating,
            date,
            popularity,
            freeDelivery,
        :param query_set: queryset of products to annotate
        :return: queryset with new fields
        """
        qs = query_set.annotate(rating=Avg('review__rate'))\
            .annotate(reviews=Count('review'))\
            .annotate(date=F("release_date"))

        # todo remove to other place. it is not for shortProduct
        # number of products sold
        sales = order_models.OrderedProduct.objects\
            .filter(product=OuterRef("pk"))\
            .filter(order__status=order_models.Order.Statuses.COMPLETED)\
            .values("product")\
            .annotate(sales=Sum("count")).values("sales")
        qs = qs.annotate(popularity=Subquery(sales))

        boundary = conf_selectors.AdminConfigSelector()\
            .boundary_of_free_delivery
        if boundary:
            qs = qs.annotate(
                freeDelivery=Case(
                    When(
                        price__gte=boundary,
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
        else:
            qs = qs.annotate(freeDelivery=False)

        return qs

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
        qs = self._annotate_for_product_short_view(query_set=qs)
        return qs

    def get_popular_products(self) -> QuerySet[models.Product]:
        """
        Returns products sorted by number of amount sold, and limited
        by POPULAR_PRODUCTS_LIMIT
        :return: annotated qs
        """
        qs = self.get_catalog(sort_field='popularity')
        qs = qs[:POPULAR_PRODUCTS_LIMIT]
        return qs

    def get_limited_products(self) -> QuerySet[models.Product]:
        """
        Returns products with attribute `limited_edition` = True, and limited
        by LIMITED_PRODUCTS_LIMIT
        :return: annotated qs
        """
        qs = self.get_active_products()
        qs = qs.filter(limited_edition=True)
        qs = self._annotate_for_product_short_view(query_set=qs)
        qs = qs[:LIMITED_PRODUCTS_LIMIT]
        return qs
