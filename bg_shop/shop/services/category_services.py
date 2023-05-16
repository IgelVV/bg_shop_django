from typing import Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from shop import models

User = get_user_model()


class CategoryService:
    #todo вызывать по цепочке метод save у подкатегорий,
    # чтобы пересчитать depth или разрвать наследие (или оставить как есть)
    def update_or_create(
            self,
            *,
            instance: models.Category,
            commit: bool = True,
            **attrs
    ) -> models.Category:
        """#
        Set passed attributes, except of depth. Calculates depth automatically,
        based on parent. It is prohibited change depth by setting attribute.
        If `parent` is passed (None, or Instance, or id) checks and sets it.
        :param instance:
        :param commit:
        :param attrs:
        :return:
        """
        if instance is None:
            instance = models.Category()
        attrs.pop("depth", None)  # you can't set it manually
        title = attrs.get("title", instance.title)
        if "parent" in attrs:
            parent = attrs.pop("parent")
            self._set_parent(
                instance=instance,
                parent=parent,
                title=title,
            )
        instance = self._set_attributes(category=instance, **attrs)
        if commit:
            instance.full_clean()
            instance.save()
        return instance

    def _set_parent(
            self,
            instance: models.Category,
            title: str,
            parent: Optional[models.Category],
            commit: bool = False,
    ) -> models.Category:
        """

        :param instance:
        :param title:
        :param parent:
        :param commit:
        :return:
        """
        if parent:
            self._check_parent(parent=parent, title=title)
            depth = parent.depth + 1
        else:
            depth = 0
        instance.parent = parent
        instance.depth = depth
        if commit:
            instance.full_clean()
            instance.save()
        return instance

    def _check_parent(self, parent: models.Category, title: str) -> None:
        """

        :param parent:
        :param title:
        :return:
        """
        if parent.title == title:
            raise ValidationError(
                "Category can't have itself as a parent!")
        elif parent.depth >= self.get_max_depth():
            raise ValidationError(
                f"Category max depth is {self.get_max_depth()}")

    def _set_attributes(
            self, category: models.Category, **attrs) -> models.Category:
        """
        Set new attributes passed in arguments, if they are acceptable.
        :param category:
        :param attrs:
        :return:
        """
        for name, value in attrs.items():
            if hasattr(models.Category, name):
                setattr(category, name, value)
            else:
                raise AttributeError(
                    f"'Category' object has no attribute '{name}'")
        return category

    def delete(self):
        ...

    @staticmethod
    def get_max_depth():
        return models.Category.MAX_DEPTH
