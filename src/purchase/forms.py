from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit
from django import forms

from purchase.layout import BasketItemField
from purchase.models import Basket, Product

PREFIX = "product-"


class BasketForm(forms.ModelForm):
    class Meta:
        model = Basket
        fields = ["payment_method"]

    class Media:
        js = ["purchase/js/basket_form.js"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))
        self.helper.layout = Layout()
        products = {}
        basket = kwargs.get("instance")
        if basket:
            for item in basket.items.all():
                products[item.product] = item.quantity
        fields = []
        for product in Product.objects.all():
            field_name = f"{PREFIX}{product.id}"
            self.fields.update(
                {
                    field_name: forms.IntegerField(
                        label=product.name,
                        min_value=0,
                        initial=products.get(product, 0),
                    )
                }
            )
            fields.append(BasketItemField(field_name, product=product))
        self.helper.layout = Layout(
            Div(*fields, css_class="row"),
            Field("payment_method"),
        )

    def save(self, commit=True):
        instance: Basket = super().save(commit=True)
        name: str
        for name, value in self.cleaned_data.items():
            if name.startswith(PREFIX):
                product_id = int(name.removeprefix(PREFIX))
                if value > 0:
                    instance.items.update_or_create(
                        product_id=product_id, defaults={"quantity": value}
                    )
                if value == 0:
                    instance.items.filter(product_id=product_id).delete()
        return instance
