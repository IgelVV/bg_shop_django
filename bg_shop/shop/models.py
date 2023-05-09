from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")

    title = models.CharField(max_length=255, verbose_name=_("title"))
    description = models.TextField(
        max_length=5120,
        verbose_name=_("description")
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
        max_digits=8,
        decimal_places=2,
        verbose_name=_("price"),
    )
    count = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name=_("count")
    )
    date = models.DateTimeField(verbose_name=_("date"))
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
    archived = models.BooleanField(default=False, verbose_name=_("archived"))

    def __str__(self):
        return f"Product({self.pk}):{self.title}"


class Category(models.Model):
    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    title = models.CharField(max_length=255, verbose_name=_("title"))
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
        verbose_name=_("parent")
    )

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


class Specification(models.Model):
    class Meta:
        verbose_name = _("specification")
        verbose_name_plural = _("specifications")

    name = models.CharField(max_length=255, verbose_name=_("name"))
    value = models.CharField(max_length=255, verbose_name=_("value"))


class Tag(models.Model):
    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")

    name = models.CharField(max_length=255, verbose_name=_("name"))

    def __str__(self):
        return f"Tag({self.pk}):{self.name}"
