from unittest.mock import patch, call

from django.test import TestCase
from django.core.exceptions import ValidationError

from shop.models import Category
from shop.services import CategoryService


class UpdateOrCreateTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = CategoryService()

    def test_with_existing_instance(self):
        category = Category.objects.create(title="Test Category")

        new_title = "Updated Category"
        attrs = {"title": new_title}
        updated_category = self.service.update_or_create(
            instance=category, **attrs)
        self.assertEqual(updated_category.title, new_title)

    def test_with_new_instance(self):
        new_title = "New Category"
        attrs = {"title": new_title}
        new_category = self.service.update_or_create(instance=None, **attrs)
        self.assertEqual(new_category.title, new_title)

    @patch("shop.services.CategoryService._set_parent")
    @patch("shop.services.CategoryService._set_attributes")
    @patch("shop.selectors.CategorySelector.get_subcategories")
    def test_with_parent(
            self,
            mock_get_subcategories,
            mock_set_attributes,
            mock_set_parent,
    ):
        category = Category.objects.create(title="Test Category")
        parent = Category.objects.create(title="Parent Category")

        mock_set_attributes.return_value = category
        mock_get_subcategories.return_value = [1, 2]

        attrs = {"parent": parent}
        updated_category = self.service.update_or_create(
            instance=category, **attrs)

        self.assertEqual(updated_category, category)
        mock_set_attributes.assert_called_once_with(category=category, **{})
        mock_set_parent.has_calls(
            call(instance=category, parent=parent),
            call(instance=1, parent=category, commit=True),
            call(instance=2, parent=category, commit=True),
        )

    @patch("shop.services.CategoryService._set_attributes")
    @patch("shop.services.CategoryService._set_parent")
    @patch("shop.selectors.CategorySelector.get_subcategories")
    def test_parent_is_none_without_subcategories(
            self,
            mock_get_subcategories,
            mock_set_parent,
            mock_set_attributes,
    ):
        category = Category.objects.create(title="Test Category")
        attrs = {
            "title": "Updated Category",
            "parent": None,
        }

        mock_set_attributes.return_value = category
        mock_get_subcategories.return_value = []

        updated_category = self.service.update_or_create(
            instance=category, **attrs)

        self.assertEqual(updated_category, category)
        mock_set_attributes.assert_called_once_with(
            category=category,
            **{"title": "Updated Category"}
        )
        mock_set_parent.assert_called_once_with(instance=category, parent=None)

    @patch("shop.services.CategoryService._set_attributes")
    @patch("shop.services.CategoryService._set_parent")
    @patch("shop.selectors.CategorySelector.get_subcategories")
    def test_commit_false(
            self,
            mock_get_subcategories,
            mock_set_parent,
            mock_set_attributes,
    ):
        initial_title = "Test Category"
        category = Category.objects.create(title=initial_title)
        attrs = {
            "title": "Updated Category",
        }
        mock_set_attributes.return_value = category
        mock_get_subcategories.return_value = []

        updated_category = self.service.update_or_create(
            instance=category, commit=False, **attrs,)
        db_category = Category.objects.get(pk=category.pk)

        self.assertEqual(updated_category.title, attrs["title"])
        self.assertEqual(db_category.title, initial_title)
        mock_set_attributes.assert_called_once_with(
            category=category,
            **{"title": "Updated Category"}
        )
        mock_get_subcategories.assert_not_called()
        mock_set_parent.assert_not_called()


class SetParentTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = CategoryService()

    @patch("shop.services.CategoryService._check_parent")
    @patch("shop.selectors.CategorySelector.get_subcategories")
    def test_set_parent_with_new_parent(
            self,
            mock_get_subcategories,
            mock_check_parent,
    ):
        category = Category.objects.create(title="Test Category")
        parent = Category.objects.create(title="Parent Category")

        updated_category = self.service._set_parent(
            instance=category, parent=parent)

        self.assertEqual(updated_category.parent, parent)
        self.assertEqual(updated_category.depth, parent.depth + 1)
        mock_check_parent.assert_called_once_with(
            parent=parent, title=category.title)
        mock_get_subcategories.assert_not_called()

    @patch("shop.services.CategoryService._check_parent")
    @patch("shop.selectors.CategorySelector.get_subcategories")
    def test_set_parent_with_parent_none(
            self,
            mock_get_subcategories,
            mock_check_parent,
    ):
        category = Category.objects.create(title="Test Category")

        updated_category = self.service._set_parent(
            instance=category, parent=None)
        self.assertEqual(updated_category.parent, None)
        self.assertEqual(updated_category.depth, 0)

        mock_check_parent.assert_not_called()
        mock_get_subcategories.assert_not_called()

    @patch("shop.services.CategoryService._check_parent")
    @patch("shop.selectors.CategorySelector.get_subcategories")
    def test_set_parent_with_new_parent_commit_true(
            self,
            mock_get_subcategories,
            mock_check_parent,
    ):
        category = Category.objects.create(title="Test Category")
        parent = Category.objects.create(title="Parent Category")

        mock_get_subcategories.return_values = []

        updated_category = self.service._set_parent(
            instance=category, parent=parent, commit=True)

        db_category = Category.objects.get(pk=category.pk)
        self.assertEqual(updated_category, db_category)
        self.assertEqual(updated_category.parent, parent)
        self.assertEqual(updated_category.depth, parent.depth + 1)

        mock_check_parent.assert_called_once_with(
            parent=parent, title=category.title)
        mock_get_subcategories.assert_called_once_with(category_id=category.pk)


class CheckParentTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = CategoryService()

    def test_check_parent_with_same_title(self):
        parent = Category.objects.create(title="Test Category")

        with self.assertRaises(ValidationError):
            self.service._check_parent(parent=parent, title=parent.title)

    def test_check_parent_with_max_depth(self):
        parent = Category.objects.create(
            title="Test Category", depth=Category.MAX_DEPTH)

        with self.assertRaises(ValidationError):
            self.service._check_parent(parent=parent, title="Child Category")

    def test_check_parent_with_valid_parent(self):
        parent = Category.objects.create(title="Test Category", depth=0)

        # Should not raise ValidationError
        self.service._check_parent(parent=parent, title="Child Category")


class SetAttributesTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = CategoryService()

    def test_set_attributes_with_valid_attrs(self):
        category = Category.objects.create(title="Test Category")

        attrs = {"title": "Updated Category", "is_active": False}
        updated_category = self.service._set_attributes(
            category=category, **attrs)
        self.assertEqual(updated_category.title, "Updated Category")
        self.assertFalse(updated_category.is_active)

    def test_set_attributes_with_invalid_attrs(self):
        category = Category.objects.create(title="Test Category")

        attrs = {"invalid_attribute": "Invalid Value"}
        with self.assertRaises(AttributeError):
            self.service._set_attributes(category=category, **attrs)


class DeleteTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = CategoryService()

    def test_delete_with_hard_option(self):
        category = Category.objects.create(title="Test Category")
        subcategory = Category.objects.create(
            title="Subcategory", parent=category)

        self.service.delete(instance=category, hard=True)
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())
        self.assertFalse(Category.objects.get(pk=subcategory.pk).is_active)

    def test_delete_without_hard_option(self):
        category = Category.objects.create(title="Test Category")
        subcategory = Category.objects.create(
            title="Subcategory", parent=category)

        self.service.delete(instance=category)
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())
        self.assertTrue(Category.objects.filter(pk=subcategory.pk).exists())
        self.assertFalse(category.is_active)
        self.assertTrue(subcategory.is_active)


class GetMaxDepthTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = CategoryService()

    def test_get_max_depth(self):

        max_depth = self.service.get_max_depth()
        self.assertEqual(max_depth, Category.MAX_DEPTH)

