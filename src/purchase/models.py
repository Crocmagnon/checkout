from __future__ import annotations

import hashlib
import uuid

from django.db import models
from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
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
                    * F("baskets__items__unit_price_cents"),
                ),
                0,
            ),
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
        ordering = ("name",)

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
            ),
        )

    def with_sold(self):
        return self.annotate(sold=Coalesce(Sum("basket_items__quantity"), 0))

    def with_fixed_price(self):
        return self.exclude(unit_price_cents=0)

    def with_no_fixed_price(self):
        return self.filter(unit_price_cents=0)


class ProductManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Product(Model):
    name = models.CharField(max_length=250, unique=True, verbose_name=_("name"))
    unit_price_cents = models.PositiveIntegerField(
        verbose_name=_("unit price (cents)"),
        help_text=_(
            "Unit price in cents. Use zero to denote that the product has no fixed price.",
        ),
    )
    initials = models.CharField(
        max_length=10,
        verbose_name=_("initials"),
        blank=False,
        null=False,
    )
    display_order = models.PositiveIntegerField(
        default=default_product_display_order,
        verbose_name=_("display order"),
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
            hashlib.sha256(bytes(self.name, encoding="utf-8")).hexdigest()[:2],
            base=16,
        )

    @property
    def has_fixed_price(self) -> bool:
        return self.unit_price_cents > 0


class BasketQuerySet(models.QuerySet):
    def priced(self) -> BasketQuerySet:
        return self.annotate(
            price=Coalesce(Sum(F("items__quantity") * F("items__unit_price_cents")), 0),
        )

    def average_basket(self) -> float:
        return self.priced().aggregate(avg=Avg("price"))["avg"]

    def by_date(self, date) -> BasketQuerySet:
        return self.filter(created_at__date=date)

    def turnover(self) -> int:
        return self.priced().aggregate(total=Sum("price"))["total"]


class Basket(Model):
    payment_method = models.ForeignKey(
        to=PaymentMethod,
        on_delete=models.PROTECT,
        related_name="baskets",
        null=False,
        blank=False,
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


class Cache(SingletonModel):
    etag = models.UUIDField(default=uuid.uuid4)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.etag)

    def refresh(self):
        self.etag = uuid.uuid4()
        self.save()


def reports_etag(_request):
    return str(Cache.get_solo().etag)


def reports_last_modified(_request):
    return Cache.get_solo().last_modified
