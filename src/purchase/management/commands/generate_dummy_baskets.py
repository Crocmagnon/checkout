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
        methods_weights = [random.randint(1, 6) for _ in range(len(payment_methods))]
        products_weights = [1 / product.display_order for product in products]
        for _ in range(count):
            method = None
            if random.random() < 0.99:
                method = random.choices(payment_methods, weights=methods_weights)[0]
            basket = Basket.objects.create(payment_method=method)
            items = []
            item_count = int(random.normalvariate(3, 2))
            for _ in range(item_count):
                product: Product = random.choices(products, weights=products_weights)[0]
                items.append(
                    BasketItem(
                        product=product,
                        basket=basket,
                        quantity=random.randint(1, 3),
                        unit_price_cents=product.unit_price_cents,
                    )
                )
            BasketItem.objects.bulk_create(items)
        return count
