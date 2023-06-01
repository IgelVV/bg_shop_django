from typing import Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from shop import models, selectors

User = get_user_model()


class CategoryService:
    def update_or_create(
            self,
            *,
            instance: models.Category,
            commit: bool = True,
            **attrs
    ) -> models.Category:
        """
        Set passed attributes, except of depth. Calculates depth automatically,
        based on parent. It is prohibited change depth by setting attribute.
        If `parent` is passed (None, or Instance, or id) checks and sets it.
        :param instance: object to update
        :param commit: if False, does not save() and does not validate
        :param attrs: can contain fields of Category model
        :return: Category with changed attributes
        """
        if instance is None:
            instance = models.Category()
        attrs.pop("depth", None)  # you can't set it manually
        new_title = attrs.get("title", None)
        if new_title:
            instance.title = new_title
        if "parent" in attrs:
            parent = attrs.pop("parent")
            self._set_parent(
                instance=instance,
                parent=parent,
            )
        instance = self._set_attributes(category=instance, **attrs)
        if commit:
            instance.full_clean()
            instance.save()
            subcategories = selectors.CategorySelector()\
                .get_subcategories(category_id=instance.pk)
            for subcategory in subcategories:
                self._set_parent(
                    instance=subcategory, parent=instance, commit=True)
        return instance

    def _set_parent(
            self,
            instance: models.Category,
            parent: Optional[models.Category],
            commit: bool = False,
    ) -> models.Category:
        """
        Change `parent` field of Category instance (even can set it None)
        :param instance: Category to change `parent`
        :param parent: new parent or None to delete relation
        :param commit: if False, does not save() and does not validate
        :return: passed Category with changed parent
        """
        if parent:
            self._check_parent(parent=parent, title=instance.title)
            depth = parent.depth + 1
        else:
            depth = 0
        instance.parent = parent
        instance.depth = depth
        if commit:
            instance.full_clean()
            instance.save()
            subcategories = selectors.CategorySelector()\
                .get_subcategories(category_id=instance.pk)
            for subcategory in subcategories:
                self._set_parent(
                    instance=subcategory, parent=instance, commit=True)
        return instance

    def _check_parent(self, parent: models.Category, title: str) -> None:
        """
        Validates that Category can be a parent for other category
        with passed title.
        Does two checks:
            1) parent does not have the same title
            (that mean it is the same obj, as titles are unique)
            2) parent does not have max depth (so child would break the rule)
        :param parent: Category instance to check
        :param title: `title` field of expected child
        :return: None
        :raises ValidationError: if one of checks are failed.
        """
        if parent.title == title:
            raise ValidationError(
                f"<{parent}> Category can't have itself as a parent!")
        elif parent.depth >= self.get_max_depth():
            raise ValidationError(
                f"<{parent}> Parent's depth must be less"
                f" than max depth ({self.get_max_depth()})")

    def _set_attributes(
            self, category: models.Category, **attrs) -> models.Category:
        """
        Set new attributes for Category obj. passed in arguments,
        if they are acceptable. Does not save the object.
        :param category: instance of Category to change
        :param attrs: attrs for Category to set
        :return: the same object
        """
        for name, value in attrs.items():
            if hasattr(models.Category, name):
                setattr(category, name, value)
            else:
                raise AttributeError(
                    f"'Category' object has no attribute '{name}'")
        return category

    def delete(self, instance: models.Category, hard: bool = False) -> None:
        """
        Deactivates all descendants (all children recursively),
        but doesn't change their depth.
        :param instance: Category obj to delete
        :param hard: if True, deletes from database,
        if False, sets is_active=False
        :return: None
        """
        descendants = selectors.CategorySelector()\
            .get_all_descendants(category_id=instance.pk)
        for descendant in descendants:
            descendant.is_active = False
            descendant.save()
        if hard:
            instance.delete()
        else:
            instance.is_active = False
            instance.save()

    @staticmethod
    def get_max_depth():
        """Returns MAX_DEPTH constant, that defines nesting.
        0 - means flat structure"""
        return models.Category.MAX_DEPTH
