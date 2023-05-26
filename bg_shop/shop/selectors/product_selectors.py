from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import (
    Avg,
    Count,
    QuerySet,
    Case,
    When,
    Value,
    F,
    BooleanField,
)

from shop import models
from shop import filters as shop_filters
from dynamic_config import selectors as conf_selectors

User = get_user_model()

POPULAR_PRODUCTS_LIMIT = 8  # todo remove to settings (or conf)
POPULAR_LIMITED_LIMIT = POPULAR_PRODUCTS_LIMIT


class ProductSelector:
    def get_viewed_products(self, user: User) -> QuerySet:
        ...

    def get_active_products(self) -> QuerySet:
        return models.Product.objects.filter(is_active=True)

    def get_rating(self, product_id: int) -> float:
        reviews = models.Review.objects\
            .filter(product_id=product_id)\
            .aggregate(Avg("rate"))
        return reviews["rate__avg"]

    def is_free_delivery(self, product: models.Product) -> bool:
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
        # todo change rating to popularity (number of sold) and reviews to rating
        qs = query_set.annotate(rating=Avg('review__rate'))\
            .annotate(reviews=Count('review'))\
            .annotate(date=F("release_date"))

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
        """"""
        if (order is None) or (order == 'dec'):
            sort_field = "-" + sort_field
        elif order == 'inc':
            pass
        else:
            raise ValueError(f"Argument `order` should be str('inc'), "
                             f"str('dec') or None type, but '{order}' instead")
        query_set = query_set.order_by(sort_field)
        return query_set

    def get_products_in_banners(self):
        qs = models.Product.objects.filter(banner__isnull=False)
        qs = self._annotate_for_product_short_view(query_set=qs)
        return qs

    def get_popular_products(self):
        qs = self.get_catalog(sort_field='rating')  # todo change to popularity (number of sold)
        qs = qs[:POPULAR_PRODUCTS_LIMIT]
        return qs

    def get_limited_products(self):
        qs = self.get_active_products()
        qs = qs.filter(limited_edition=True)
        qs = self._annotate_for_product_short_view(query_set=qs)
        qs = qs[:POPULAR_LIMITED_LIMIT]
        return qs


