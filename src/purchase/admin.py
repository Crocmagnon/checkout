from django.contrib import admin
from django.contrib.admin import register

from purchase.models import Basket, BasketItem, PaymentMethod, Product
from purchase.templatetags.purchase import currency


@register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "display_order", "unit_price", "sold", "turnover"]
    list_editable = ["display_order"]
    search_fields = ["name"]

    def get_queryset(self, request):
        return super().get_queryset(request).with_sold().with_turnover()

    def unit_price(self, instance: Product):
        return currency(instance.unit_price_cents)

    def sold(self, instance: Product):
        return instance.sold

    def turnover(self, instance: Product):
        return currency(instance.turnover)


@register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["name", "turnover"]
    search_fields = ["name"]

    def get_queryset(self, request):
        return super().get_queryset(request).with_turnover()

    def turnover(self, instance: Product):
        return currency(instance.turnover)


class BasketItemInline(admin.TabularInline):
    model = BasketItem
    fields = ["product", "quantity", "price"]
    extra = 0
    readonly_fields = ["price"]

    def get_queryset(self, request):
        return super().get_queryset(request).priced()

    def price(self, instance) -> str:
        return currency(instance.price)


@register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ["id", "payment_method", "created_at", "price"]
    fields = ["created_at", "payment_method", "price"]
    list_filter = ["payment_method"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "price"]
    inlines = [BasketItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).priced()

    def price(self, instance) -> str:
        return currency(instance.price)
