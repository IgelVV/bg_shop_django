from django.contrib.auth import get_user_model

from shop import models

User = get_user_model()


class CategoryService:
    def create_category(self):
        ...

    def update_category(self):
        ...

    def delete_category(self):
        ...

    @staticmethod
    def get_max_depth():
        return models.Category.MAX_DEPTH



