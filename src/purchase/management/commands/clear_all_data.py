from django.core.management.base import BaseCommand

from purchase.models import (
    Basket,
    BasketItem,
    Cache,
    PaymentMethod,
    Product,
    ProductCategory,
)


class Command(BaseCommand):
    help = "Clear all data"

    def handle(self, *args, **options):  # noqa: ARG002
        self.delete(BasketItem)
        self.delete(Basket)
        self.delete(Product)
        self.delete(PaymentMethod)
        self.delete(ProductCategory)
        Cache.get_solo().refresh()

    def delete(self, cls):
        _, count = cls.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"Successfully deleted {count} {cls}."))
