from django.db.models import Avg, Sum
from django.views.generic import TemplateView

from purchase.models import Basket, PaymentMethod, Product
from purchase.views.utils import ProtectedViewsMixin


class ReportsView(ProtectedViewsMixin, TemplateView):
    permission_required = ["purchase.view_basket"]
    template_name = "purchase/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = Basket.objects.values_list("created_at__date", flat=True).distinct()
        average_basket_by_day = {
            date: Basket.objects.by_date(date).average_basket() for date in dates
        }
        turnover_by_day = {
            date: Basket.objects.by_date(date).turnover() for date in dates
        }

        context.update(
            {
                "turnover": Basket.objects.turnover(),
                "turnover_by_day": turnover_by_day,
                "average_basket": Basket.objects.average_basket(),
                "average_basket_by_day": average_basket_by_day,
                "products": Product.objects.with_turnover().with_sold(),
                "payment_methods": PaymentMethod.objects.with_turnover().with_sold(),
                "no_payment_method": Basket.objects.no_payment_method().priced(),
            }
        )
        return context
