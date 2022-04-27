import datetime
from io import StringIO

from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from matplotlib import pyplot as plt
from matplotlib import ticker

from purchase.models import Basket, PaymentMethod, Product, ProductQuerySet
from purchase.views.utils import ProtectedViewsMixin


class ReportsView(ProtectedViewsMixin, TemplateView):
    permission_required = ["purchase.view_basket"]
    template_name = "purchase/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        baskets = list(Basket.objects.priced().order_by("created_at"))
        if not baskets:
            messages.warning(self.request, _("No sale to report"))
            return context

        dates = Basket.objects.values_list("created_at__date", flat=True).distinct()
        average_basket_by_day = {
            date: Basket.objects.by_date(date).average_basket() for date in dates
        }
        turnover_by_day = {
            date: Basket.objects.by_date(date).turnover() for date in dates
        }

        products = Product.objects.with_turnover().with_sold()
        products_plot = self.get_products_plot(products)
        by_hour_plot = self.by_hour_plot(baskets)
        context.update(
            {
                "turnover": Basket.objects.turnover(),
                "turnover_by_day": turnover_by_day,
                "average_basket": Basket.objects.average_basket(),
                "average_basket_by_day": average_basket_by_day,
                "products": products,
                "products_plot": products_plot,
                "by_hour_plot": by_hour_plot,
                "payment_methods": PaymentMethod.objects.with_turnover().with_sold(),
                "no_payment_method": Basket.objects.no_payment_method().priced(),
            }
        )
        return context

    def get_products_plot(self, products: ProductQuerySet):
        labels = []
        sold = []
        turnover = []
        for product in products:
            labels.append(product.name)
            sold.append(product.sold)
            turnover.append(product.turnover / 100)

        fig, ax1 = plt.subplots()
        color = "tab:orange"
        ax1.bar(labels, sold, width=0.8, color=color)
        ax1.tick_params(axis="x", rotation=15)
        ax1.set_ylabel(_("# sold"), color=color)

        color = "tab:blue"
        ax2 = ax1.twinx()
        ax2.bar(labels, turnover, width=0.4, color=color)
        ax2.set_ylabel(_("Turnover by product"), color=color)
        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f€"))

        fig.tight_layout()
        image_data = StringIO()
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
            while basket.created_at < end_slot:
                count += 1
                turnover += basket.price / 100
                basket_index += 1
                if basket_index == len(baskets):
                    break
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
