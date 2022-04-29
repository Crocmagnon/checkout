from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.utils.translation import gettext as _

from purchase.layout import BasketItemField
from purchase.models import Basket, Product

PREFIX = "product-"


class BasketForm(forms.ModelForm):
    class Meta:
        model = Basket
        fields = ["payment_method"]
        widgets = {"payment_method": forms.RadioSelect}

    class Media:
        js = ["purchase/js/basket_form.js"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.add_input(Submit("submit", _("Save")))
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
            Div(
                *fields,
                css_class="row row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5 row-cols-xl-6 g-4",
            ),
            InlineRadios("payment_method"),
        )

    def save(self, commit=True):
        instance: Basket = super().save(commit=True)
        name: str
        products = {product.id: product for product in Product.objects.all()}
        for name, value in self.cleaned_data.items():
            if name.startswith(PREFIX):
                product_id = int(name.removeprefix(PREFIX))
                product = products[product_id]
                if value > 0:
                    instance.items.update_or_create(
                        product=product,
                        defaults={
                            "quantity": value,
                            "unit_price_cents": product.unit_price_cents,
                        },
                    )
                if value == 0:
                    instance.items.filter(product=product).delete()
        return instance
