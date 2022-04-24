from crispy_forms.layout import Field


class BasketItemField(Field):
    template = "purchase/basket_item.html"

    def __init__(self, *args, product, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product

    def render(self, *args, **kwargs):
        extra_context = kwargs.get("extra_context", {})
        extra_context.update({"product": self.product})
        kwargs["extra_context"] = extra_context
        return super().render(*args, **kwargs)
