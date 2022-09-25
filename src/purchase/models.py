from __future__ import annotations

import hashlib
import uuid

from django.db import models
from django.db.models import Avg, Count, F, Sum, UniqueConstraint
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageOps
from solo.models import SingletonModel


class Model(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))

    class Meta:
        abstract = True


class PaymentMethodQuerySet(models.QuerySet):
    def with_turnover(self):
        return self.annotate(
            turnover=Coalesce(
                Sum(
                    F("baskets__items__quantity")
                    * F("baskets__items__unit_price_cents")
                ),
                0,
            )
        )

    def with_sold(self):
        return self.annotate(sold=Count("baskets", distinct=True))


class PaymentMethodManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class PaymentMethod(Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("name"))

    objects = PaymentMethodManager.from_queryset(PaymentMethodQuerySet)()

    class Meta:
        verbose_name = _("payment method")
        verbose_name_plural = _("payment methods")

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


def default_product_display_order():
    last = Product.objects.last()
    if last is None:
        return 1
    return last.display_order + 1


class ProductQuerySet(models.QuerySet):
    def with_turnover(self):
        return self.annotate(
            turnover=Coalesce(
                Sum(F("basket_items__quantity") * F("basket_items__unit_price_cents")),
                0,
            )
        )

    def with_sold(self):
        return self.annotate(sold=Coalesce(Sum("basket_items__quantity"), 0))


class ProductManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Product(Model):
    name = models.CharField(max_length=250, unique=True, verbose_name=_("name"))
    image = models.ImageField(null=True, blank=True, verbose_name=_("image"))
    unit_price_cents = models.PositiveIntegerField(
        verbose_name=_("unit price (cents)"), help_text=_("unit price in cents")
    )
    display_order = models.PositiveIntegerField(
        default=default_product_display_order, verbose_name=_("display order")
    )

    objects = ProductManager.from_queryset(ProductQuerySet)()

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    @property
    def color_hue(self):
        return int(
            hashlib.sha256(bytes(self.name, encoding="utf-8")).hexdigest()[:2], base=16
        )

    def save(self, *args, **kwargs):
        super().save()
        if not self.image:
            return
        with Image.open(self.image.path) as img:
            img = ImageOps.exif_transpose(img)

            width, height = img.size  # Get dimensions

            if width > 300 and height > 300:
                # keep ratio but shrink down
                img.thumbnail((width, height))

            # check which one is smaller
            if height < width:
                # make square by cutting off equal amounts left and right
                left = (width - height) / 2
                right = (width + height) / 2
                top = 0
                bottom = height
                img = img.crop((left, top, right, bottom))

            elif width < height:
                # make square by cutting off bottom
                left = 0
                right = width
                top = 0
                bottom = width
                img = img.crop((left, top, right, bottom))

            if width > 300 and height > 300:
                img.thumbnail((300, 300))

            img.save(self.image.path)


class BasketQuerySet(models.QuerySet):
    def priced(self) -> BasketQuerySet:
        return self.annotate(
            price=Coalesce(Sum(F("items__quantity") * F("items__unit_price_cents")), 0)
        )

    def average_basket(self) -> float:
        return self.priced().aggregate(avg=Avg("price"))["avg"]

    def by_date(self, date) -> BasketQuerySet:
        return self.filter(created_at__date=date)

    def turnover(self) -> int:
        return self.priced().aggregate(total=Sum("price"))["total"]

    def no_payment_method(self) -> BasketQuerySet:
        return self.filter(payment_method=None)


class Basket(Model):
    payment_method = models.ForeignKey(
        to=PaymentMethod,
        on_delete=models.PROTECT,
        related_name="baskets",
        null=True,
        blank=True,
        verbose_name=_("payment method"),
    )

    objects = BasketQuerySet.as_manager()

    class Meta:
        verbose_name = _("basket")
        verbose_name_plural = _("baskets")

    def __str__(self):
        return gettext("Basket #%(id)s") % {"id": self.id}

    def get_absolute_url(self):
        return reverse("purchase:update", args=(self.pk,))


class BasketItemQuerySet(models.QuerySet):
    def priced(self):
        return self.annotate(price=Coalesce(F("quantity") * F("unit_price_cents"), 0))


class BasketItem(Model):
    product = models.ForeignKey(
        to=Product,
        on_delete=models.PROTECT,
        related_name="basket_items",
        verbose_name=_("product"),
    )
    basket = models.ForeignKey(
        to=Basket,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("basket"),
    )
    quantity = models.PositiveIntegerField(verbose_name=_("quantity"))
    unit_price_cents = models.PositiveIntegerField(
        verbose_name=_("unit price (cents)"),
        help_text=_("product's unit price in cents at the time of purchase"),
    )

    objects = BasketItemQuerySet.as_manager()

    class Meta:
        verbose_name = _("basket item")
        verbose_name_plural = _("basket items")
        constraints = [
            UniqueConstraint("product", "basket", name="unique_product_per_basket")
        ]


class CacheEtag(SingletonModel):
    value = models.UUIDField(default=uuid.uuid4)

    def __str__(self) -> str:
        return str(self.value)

    def refresh(self):
        self.value = uuid.uuid4()
        self.save()
