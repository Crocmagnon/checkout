from django.db.models import Sum
from django.views.generic import TemplateView

from purchase.models import Basket, PaymentMethod, Product


class ReportsView(TemplateView):
    template_name = "purchase/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "total": Basket.objects.priced().aggregate(total=Sum("price"))["total"],
                "by_day": {},
                "products": Product.objects.with_turnover().with_sold(),
                "payment_methods": PaymentMethod.objects.with_turnover(),
            }
        )
        return context
