from crispy_forms import layout
from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.urls import reverse
from django.utils.translation import gettext as _

from purchase.layout import BasketItemField
from purchase.models import Basket, Product

PRICED_PREFIX = "product-"
UNPRICED_PREFIX = "unpriced_product-"


class BasketForm(forms.ModelForm):
    class Meta:
        model = Basket
        fields = ["payment_method"]
        widgets = {"payment_method": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.add_input(Submit("submit", _("Save")))
        self.helper.attrs = {
            "hx_post": reverse("purchase:price_preview"),
            "hx_trigger": "keyup delay:500ms,change delay:500ms",
            "hx_target": "#price_preview",
            "hx_swap": "innerHTML",
        }
        self.helper.layout = Layout()
        products = {}
        basket = kwargs.get("instance")
        if basket:
            for item in basket.items.all():
                products[item.product] = item.quantity
        fields = []
        for product in Product.objects.with_category().with_fixed_price():
            field_name = f"{PRICED_PREFIX}{product.id}"
            self.fields.update(
                {
                    field_name: forms.IntegerField(
                        label=product.name,
                        min_value=0,
                        initial=products.get(product, 0),
                    ),
                },
            )
            fields.append(BasketItemField(field_name, product=product))
        total = 0
        count = 0
        if basket:
            total = basket.price / 100
            count = basket.articles_count
        self.helper.layout = Layout(
            Div(
                *fields,
                css_class="row row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5 row-cols-xl-6 g-4",
                css_id="products",
            ),
            InlineRadios("payment_method"),
            Div(
                layout.HTML(
                    f"Montant total : {total:.2f}€<br>Nombre d'articles: {count}",
                ),
                css_id="price_preview",
                css_class="mb-2",
            ),
        )

    def save(self):
        instance: Basket = super().save(commit=True)
        name: str
        products = {product.id: product for product in Product.objects.all()}
        for name, value in self.cleaned_data.items():
            if name.startswith(PRICED_PREFIX):
                product_id = int(name.removeprefix(PRICED_PREFIX))
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
