from typing import Optional
from django.db import models as db_models

from shop import models


class CategorySelector:
    """Category has self reference to implement tree structure."""
    @staticmethod
    def get_root_categories_queryset(
            only_active: bool = True) -> db_models.QuerySet:
        """
        Returns categories witch have no parent.
        :param only_active: if True, ignores categories with field active=False
        :return: queryset with categories without parent
        """
        queryset = models.Category.objects\
            .select_related('image')\
            .select_related('parent').filter(parent=None)
        if only_active:
            queryset = queryset.filter(is_active=True)
        return queryset

    @staticmethod
    def get_subcategories(
            category_id: int,
            only_active: bool = True,
    ) -> db_models.QuerySet:
        """
        Returns only directly related records.
        :param category_id: id that the subcategories should be associated with
        :param only_active: if True, ignores categories with field active=False
        :return: categories witch have reference to this category
            in field parent
        """
        queryset = models.Category.objects.filter(parent=category_id)
        if only_active:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_all_descendants(
            self,
            category_id: int,
            only_active: bool = True,
    ) -> list[models.Category]:
        """
        Returns all subcategories recursively.
        :param category_id: start of chain
        :param only_active: for checking is_active attribute
        :return: tree of categories with one root category
        """
        result = list()
        children = self.get_subcategories(
                category_id=category_id, only_active=only_active)
        result.extend(list(children))
        for child in children:
            sub_descendants = self.get_all_descendants(
                category_id=child.id, only_active=only_active)
            result.extend(sub_descendants)
        return result

    # def get_category_tree(
    #         self,
    #         start_node_id: int = None,
    #         only_active: bool = True,
    #         depth: int = 10,
    #         formatter: Callable = None,
    # ) -> list[Optional[dict[str, Any]]]:
    #     """
    #     Returns categories as a tree.
    #     If start_node_id is not passed returns all categories.
    #     :param depth:
    #     :param start_node_id:
    #     :param only_active: If False returns all categories (from start node)
    #     :return:
    #     """
    #     queryset = models.Category.objects\
    #         .select_related('image')\
    #         .select_related('parent')
    #     # to do get specific fields and rename
    #     if only_active:
    #         queryset =queryset.filter(is_active=True)
    #     if start_node_id:
    #         queryset = queryset.filter(id=start_node_id)
    #     else:
    #         queryset = queryset.filter(depth=0)
    #
    #     values = list(queryset.values())
    #     for category in values:
    #         category['subcategories'] = []
    #         if depth > 0:
    #             subcategories = self._get_subcategories(
    #                 category_id=category["id"], only_active=only_active)
    #             for subcategory in subcategories:
    #                 subcategory_info = self.get_category_tree(
    #                     start_node_id=subcategory.id,
    #                     only_active=only_active,
    #                     depth=depth-1,
    #                 )
    #                 category['subcategories'].extend(subcategory_info)
    #     return values

