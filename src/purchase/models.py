from django.db import models
from django.urls import reverse


class Model(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PaymentMethod(Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


def default_product_display_order():
    return Product.objects.last().display_order + 1


class Product(Model):
    name = models.CharField(max_length=250, unique=True)
    image = models.ImageField(null=True, blank=True)
    unit_price_cents = models.PositiveIntegerField()
    display_order = models.PositiveIntegerField(default=default_product_display_order)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class Basket(Model):
    payment_method = models.ForeignKey(
        to=PaymentMethod,
        on_delete=models.PROTECT,
        related_name="baskets",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Panier #{self.id}"

    @property
    def price(self) -> int:
        return sum(item.price for item in self.items.all())

    @property
    def price_display(self) -> str:
        price = self.price / 100
        return f"{price}€"

    def get_absolute_url(self):
        return reverse("purchase:update", args=(self.pk,))


class BasketItem(Model):
    product = models.ForeignKey(
        to=Product, on_delete=models.PROTECT, related_name="basket_items"
    )
    basket = models.ForeignKey(
        to=Basket, on_delete=models.CASCADE, related_name="items"
    )
    quantity = models.PositiveIntegerField()

    @property
    def price(self) -> int:
        return self.product.unit_price_cents * self.quantity

    @property
    def price_display(self) -> str:
        price = self.price / 100
        return f"{price}€"
