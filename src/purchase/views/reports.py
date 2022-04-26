import datetime
from io import StringIO

from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from matplotlib import pyplot as plt
from matplotlib import ticker

from purchase.models import (
    Basket,
    BasketQuerySet,
    PaymentMethod,
    Product,
    ProductQuerySet,
)
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

        products = Product.objects.with_turnover().with_sold()
        products_sold_plot = self.get_products_sold_plot(products)
        products_turnover_plot = self.get_products_turnover_plot(products)
        baskets = list(Basket.objects.priced().order_by("created_at"))
        by_hour_plot = self.by_hour_plot(baskets)
        context.update(
            {
                "turnover": Basket.objects.turnover(),
                "turnover_by_day": turnover_by_day,
                "average_basket": Basket.objects.average_basket(),
                "average_basket_by_day": average_basket_by_day,
                "products": products,
                "products_sold_plot": products_sold_plot,
                "products_turnover_plot": products_turnover_plot,
                "by_hour_plot": by_hour_plot,
                "payment_methods": PaymentMethod.objects.with_turnover().with_sold(),
                "no_payment_method": Basket.objects.no_payment_method().priced(),
            }
        )
        return context

    def get_products_sold_plot(self, products: ProductQuerySet):
        labels = []
        values = []
        for product in products:
            labels.append(product.name)
            values.append(product.sold)
        fig = plt.figure()
        plt.bar(labels, values)
        plt.xticks(rotation=15)
        image_data = StringIO()
        plt.title(_("# sold"))
        fig.savefig(image_data, format="svg")
        image_data.seek(0)
        return image_data.getvalue()

    def get_products_turnover_plot(self, products: ProductQuerySet):
        labels = []
        values = []
        for product in products:
            labels.append(product.name)
            values.append(product.turnover / 100)
        fig = plt.figure()
        plt.bar(labels, values)
        plt.xticks(rotation=15)
        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f€"))
        image_data = StringIO()
        plt.title(_("Turnover"))
        fig.savefig(image_data, format="svg")
        image_data.seek(0)
        return image_data.getvalue()

    def by_hour_plot(self, baskets):
        current: datetime.datetime = baskets[0].created_at
        current = current.replace(minute=0, second=0, microsecond=0)
        end: datetime.datetime = baskets[-1].created_at
        basket_index = 0
        labels = []
        counts = []
        turnovers = []
        while current < end:
            end_slot = current + datetime.timedelta(hours=1)
            basket = baskets[basket_index]
            count = 0
            turnover = 0
            while basket.created_at < end_slot and basket_index < len(baskets) - 1:
                count += 1
                turnover += basket.price / 100
                basket_index += 1
                basket = baskets[basket_index]
            labels.append(current)
            counts.append(count)
            turnovers.append(turnover)
            current = end_slot
        fig, ax1 = plt.subplots()
        hours_in_day = 24
        color = "tab:orange"
        ax1.bar(labels, counts, width=1 / hours_in_day, color=color)
        ax1.tick_params(axis="x", rotation=15)
        ax1.set_ylabel(_("Basket count by hour"), color=color)

        color = "tab:blue"
        ax2 = ax1.twinx()
        ax2.bar(labels, turnovers, width=1 / (hours_in_day * 2), color=color)
        ax2.set_ylabel(_("Turnover by hour"), color=color)
        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f€"))

        fig.tight_layout()
        image_data = StringIO()
        fig.savefig(image_data, format="svg")
        image_data.seek(0)
        return image_data.getvalue()
