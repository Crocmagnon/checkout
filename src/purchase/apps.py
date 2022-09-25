from django.apps import AppConfig
from django.db.models.signals import post_save


class PurchaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "purchase"

    def ready(self):
        from purchase.models import Basket, BasketItem, PaymentMethod, Product

        from .signals import basket_item_on_save

        post_save.connect(basket_item_on_save, sender=BasketItem)
        post_save.connect(basket_item_on_save, sender=Basket)
        post_save.connect(basket_item_on_save, sender=Product)
        post_save.connect(basket_item_on_save, sender=PaymentMethod)
