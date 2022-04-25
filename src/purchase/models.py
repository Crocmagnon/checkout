from django.db import models
from django.db.models import Count, F, Sum
from django.urls import reverse
from PIL import Image, ImageOps


class Model(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PaymentMethodQuerySet(models.QuerySet):
    def with_turnover(self):
        return self.annotate(
            turnover=Sum(
                F("baskets__items__quantity")
                * F("baskets__items__product__unit_price_cents")
            )
        )


class PaymentMethod(Model):
    name = models.CharField(max_length=50, unique=True)

    objects = PaymentMethodQuerySet.as_manager()

    def __str__(self):
        return self.name


def default_product_display_order():
    return Product.objects.last().display_order + 1


class ProductQuerySet(models.QuerySet):
    def with_turnover(self):
        return self.annotate(
            turnover=Sum(F("basket_items__quantity") * F("unit_price_cents"))
        )

    def with_sold(self):
        return self.annotate(sold=Sum("basket_items__quantity"))


class Product(Model):
    name = models.CharField(max_length=250, unique=True)
    image = models.ImageField(null=True, blank=True)
    unit_price_cents = models.PositiveIntegerField()
    display_order = models.PositiveIntegerField(default=default_product_display_order)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save()
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
    def priced(self):
        return self.annotate(
            price=Sum(F("items__quantity") * F("items__product__unit_price_cents"))
        )


class Basket(Model):
    payment_method = models.ForeignKey(
        to=PaymentMethod,
        on_delete=models.PROTECT,
        related_name="baskets",
        null=True,
        blank=True,
    )

    objects = BasketQuerySet.as_manager()

    def __str__(self):
        return f"Panier #{self.id}"

    def get_absolute_url(self):
        return reverse("purchase:update", args=(self.pk,))


class BasketItemQuerySet(models.QuerySet):
    def priced(self):
        return self.annotate(price=F("quantity") * F("product__unit_price_cents"))


class BasketItem(Model):
    product = models.ForeignKey(
        to=Product, on_delete=models.PROTECT, related_name="basket_items"
    )
    basket = models.ForeignKey(
        to=Basket, on_delete=models.CASCADE, related_name="items"
    )
    quantity = models.PositiveIntegerField()

    objects = BasketItemQuerySet.as_manager()
