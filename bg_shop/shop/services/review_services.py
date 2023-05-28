from typing import Optional

from django.contrib.auth import get_user_model
from django.utils import timezone

from shop import models

User = get_user_model()


class ReviewService:
    def create_review(
            self,
            user_id: int,
            product_id: int,
            text: Optional[str],
            rate: int,
            date: Optional[timezone] = None,
            commit: bool = True,
    ) -> models.Review:
        """

        :param user_id:
        :param product_id:
        :param text:
        :param rate:
        :param date:
        :param commit:
        :return:
        """
        review = models.Review(
            author_id=user_id,
            product_id=product_id,
            text=text,
            rate=rate
        )
        if date:
            review.date = date
        else:
            review.date = timezone.now()
        if commit:
            review.full_clean()
            review.save()
        return review
