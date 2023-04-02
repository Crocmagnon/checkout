import random
from datetime import timedelta

import freezegun
import numpy as np
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from purchase.models import Basket, BasketItem, Cache, PaymentMethod, Product


class Command(BaseCommand):
    help = "Generates dummy baskets"  # noqa: A003

    def handle(self, *args, **options):  # noqa: ARG002
        call_command("loaddata", ["payment_methods", "products"])
        products = list(Product.objects.all())
        payment_methods = list(PaymentMethod.objects.all())

        count = 0
        hours = list(range(-29, -20))
        hours += list(range(-10, -2))
        for hour in hours:
            with freezegun.freeze_time(now() + timedelta(hours=hour)):
                count += self.generate_baskets(payment_methods, products)

        Cache.get_solo().refresh()
        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} baskets."))

    def delete(self, cls):
        _, count = cls.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"Successfully deleted {count} {cls}."))

    def generate_baskets(self, payment_methods, products):
        count = int(random.normalvariate(20, 10))
        methods_weights = [random.randint(1, 6) for _ in range(len(payment_methods))]
        products_weights = [1 / product.display_order for product in products]
        for _ in range(count):
            method = random.choices(payment_methods, weights=methods_weights)[0]
            basket = Basket.objects.create(payment_method=method)
            items_in_basket = int(random.normalvariate(3, 2))
            if items_in_basket > len(products):
                items_in_basket = len(products)
            if items_in_basket < 1:
                items_in_basket = 1
            rng = np.random.default_rng()
            selected_products = rng.choice(
                products,
                size=items_in_basket,
                replace=False,
                p=np.asarray(products_weights) / sum(products_weights),
            )
            items = []
            for product in selected_products:
                if not product.has_fixed_price:
                    items.append(
                        BasketItem(
                            product=product,
                            basket=basket,
                            quantity=1,
                            unit_price_cents=random.randint(317, 514),
                        ),
                    )
                else:
                    items.append(
                        BasketItem(
                            product=product,
                            basket=basket,
                            quantity=random.randint(1, 3),
                            unit_price_cents=product.unit_price_cents,
                        ),
                    )
            BasketItem.objects.bulk_create(items)
        return count
