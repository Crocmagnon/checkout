from django.contrib import admin
from django.contrib.admin import register

from purchase.models import Basket, BasketItem, PaymentMethod, Product


@register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "display_order", "unit_price"]
    search_fields = ["name"]

    def unit_price(self, instance: Product):
        return instance.unit_price_cents / 100


@register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


class BasketItemInline(admin.TabularInline):
    model = BasketItem
    fields = ["product", "quantity", "price"]
    extra = 0
    readonly_fields = ["price"]

    def price(self, instance) -> str:
        return instance.price_display


@register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ["id", "payment_method", "created_at", "price"]
    fields = ["created_at", "payment_method"]
    list_filter = ["payment_method"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]
    inlines = [BasketItemInline]

    def price(self, instance) -> str:
        return instance.price_display
