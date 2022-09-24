import random
from functools import partial

import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission

from common.models import User
from purchase.models import Basket, BasketItem, PaymentMethod, Product

USER_PASSWORD = "test_password"


class CashierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    password = make_password(USER_PASSWORD)
    is_active = True
    is_staff = True

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if create:
            self.groups.add(CashierGroupFactory())


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker("text", max_nb_chars=80)
    unit_price_cents = factory.LazyFunction(partial(random.randint, 80, 650))


class PaymentMethodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PaymentMethod

    name = factory.Faker("text", max_nb_chars=30)


class BasketWithItemsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Basket

    payment_method = factory.Iterator(PaymentMethod.objects.all())

    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        if create:
            products = Product.objects.order_by("?")
            quantity = random.randint(1, len(products))
            for product in products[:quantity]:
                BasketItem.objects.create(
                    product=product,
                    basket=self,
                    quantity=random.randint(1, 4),
                    unit_price_cents=product.unit_price_cents,
                )


class CashierGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = "Caissier"

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if create:
            self.permissions.add(
                Permission.objects.get(codename="add_basket"),
                Permission.objects.get(codename="change_basket"),
                Permission.objects.get(codename="delete_basket"),
                Permission.objects.get(codename="view_basket"),
                Permission.objects.get(codename="add_basketitem"),
                Permission.objects.get(codename="change_basketitem"),
                Permission.objects.get(codename="delete_basketitem"),
                Permission.objects.get(codename="view_basketitem"),
                Permission.objects.get(codename="view_paymentmethod"),
                Permission.objects.get(codename="view_product"),
            )
