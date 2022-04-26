from django.core.management.base import BaseCommand

from purchase.models import Basket, BasketItem, PaymentMethod, Product


class Command(BaseCommand):
    help = "Clear all data"  # noqa: A003

    def handle(self, *args, **options):
        self.delete(BasketItem)
        self.delete(Basket)
        self.delete(Product)
        self.delete(PaymentMethod)

    def delete(self, cls):
        _, count = cls.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"Successfully deleted {count} {cls}."))
