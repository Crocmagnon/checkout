import random
from datetime import timedelta

import freezegun
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from purchase.models import Basket, BasketItem, PaymentMethod, Product


class Command(BaseCommand):
    help = "Generates dummy baskets"  # noqa: A003

    def handle(self, *args, **options):
        call_command("loaddata", ["payment_methods", "products"])
        products = list(Product.objects.all())
        payment_methods = list(PaymentMethod.objects.all())

        count = 0
        hours = list(range(-29, -20))
        hours += list(range(-10, -2))
        for hour in hours:
            with freezegun.freeze_time(now() + timedelta(hours=hour)):
                count += self.generate_baskets(payment_methods, products)

        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} baskets."))

    def delete(self, cls):
        _, count = cls.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"Successfully deleted {count} {cls}."))

    def generate_baskets(self, payment_methods, products):
        count = int(random.normalvariate(20, 10))
        for _ in range(count):
            method = random.choice(payment_methods)
            basket = Basket.objects.create(payment_method=method)
            items = []
            item_count = int(random.normalvariate(3, 2))
            for _ in range(item_count):
                product = random.choice(products)
                items.append(
                    BasketItem(
                        product=product, basket=basket, quantity=random.randint(1, 3)
                    )
                )
            BasketItem.objects.bulk_create(items)
        return count
