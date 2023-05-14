from django.contrib.auth import get_user_model

from shop import models

User = get_user_model()


class ReviewService:
    def add_review(
        self,
        user: User,
        product: 'models.Product',
        text: str,
        rate: float
    ) -> tuple['models.Review', bool]:
        ...
