from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# todo Удаление товаров, заказов, пользователей и категорий товаров
#  осуществляется только с использованием механизма мягкого удаления.
class Product(models.Model):
    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")

    title = models.CharField(max_length=255, verbose_name=_("title"))
    description = models.TextField(
        max_length=5120,
        verbose_name=_("description"),
    )
    category = models.ForeignKey(
        "Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("category")
    )
    price = models.DecimalField(
        default=0,
        validators=[MinValueValidator(0)],
        max_digits=8,
        decimal_places=2,
        verbose_name=_("price"),
    )
    count = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name=_("count")
    )
    release_date = models.DateField(verbose_name=_("release date"))
    images = models.ManyToManyField("common.Image", verbose_name=_("images"))
    tags = models.ManyToManyField("Tag", verbose_name=_("tags"))
    specifications = models.ManyToManyField(
        "Specification", verbose_name=_("specifications"))
    sort_index = models.SmallIntegerField(
        default=0, verbose_name=_("sort index"))
    limited_edition = models.BooleanField(
        default=False, verbose_name=_("limited edition"))
    manufacturer = models.CharField(
        max_length=255,
        verbose_name=_("manufacturer")
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this product should be treated as active. "
            "Unselect this instead of deleting products."
        ),
    )

    @property
    def short_description(self):
        if self.description:
            return self.description[:255] + "..."

    def __str__(self):
        return f"Product({self.pk}):{self.title}"


class Category(models.Model):
    """
    Use service for CRUD.
    It is a simple tree structure.
    MAX_DEPTH - how many edges can be between node and root
    (or level, counted from 0).
    Parent's depth must be lower than node's one (to avoid circular reference).
    """
    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    MAX_DEPTH = 2  # from 0

    title = models.CharField(
        unique=True,
        max_length=255,
        verbose_name=_("title"),
    )
    image = models.ForeignKey(
        "common.Image",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("image")
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("parent"),
    )
    depth = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_DEPTH)],
        default=0,
        verbose_name=_("depth")
    )
    sort_index = models.SmallIntegerField(
        default=0, verbose_name=_("sort index"))
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this category should be treated as active. "
            "Unselect this instead of deleting categories."
        ),
    )

    @property
    def is_root(self) -> bool:
        return self.parent is None

    def __str__(self):
        return f"Category({self.pk}):{self.title}"


class Review(models.Model):
    class Meta:
        verbose_name = _("review")
        verbose_name_plural = _("reviews")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("author")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("product"),
    )
    text = models.TextField(
        max_length=1024,
        null=True,
        blank=True,
        verbose_name=_("text")
    )
    rate = models.SmallIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name=_("rate"),
    )
    date = models.DateTimeField(auto_now=True)


class Sale(models.Model):
    class Meta:
        verbose_name = _("sale")
        verbose_name_plural = _("sales")

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("product"),
    )
    discount = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        verbose_name=_("discount"),
    )
    date_from = models.DateField(verbose_name=_("date from"))
    date_to = models.DateField(verbose_name=_("date to"))

    def clean(self):
        if not self.date_from <= self.date_to:
            raise ValidationError("End date cannot be before start date")

    @property
    def has_started(self) -> bool:
        now = timezone.now()
        return self.date_from <= now.date()

    @property
    def has_finished(self) -> bool:
        now = timezone.now()
        return self.date_to <= now.date()

    # def is_within(self, x_date: date) -> bool:
    #     return self.date_from <= x_date <= self.date_to


class Specification(models.Model):
    class Meta:
        verbose_name = _("specification")
        verbose_name_plural = _("specifications")
        unique_together = ("name", "value",)

    name = models.CharField(max_length=255, verbose_name=_("name"))
    value = models.CharField(max_length=255, verbose_name=_("value"))

    def __str__(self):
        return f"Specification({self.pk}): {self.name}({self.value})"


class Tag(models.Model):
    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")

    name = models.CharField(max_length=255, verbose_name=_("name"))

    def __str__(self):
        return f"Tag({self.pk}):{self.name}"
