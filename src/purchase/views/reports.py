import datetime
from io import StringIO
from zoneinfo import ZoneInfo

import matplotlib
import numpy as np
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.container import BarContainer
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter, HourLocator
from matplotlib.figure import Figure

from purchase.models import Basket, PaymentMethod, Product, ProductQuerySet

matplotlib.use("SVG")


@permission_required("purchase.view_basket")
def products_plots_view(request):
    products = Product.objects.with_turnover().with_sold()
    (
        products_plot,
        products_sold_pie,
        products_turnover_pie,
    ) = get_products_plots(products)
    context = {
        "plots": [products_plot, products_sold_pie, products_turnover_pie],
    }
    return render(request, "purchase/snippets/plots.html", context)


@permission_required("purchase.view_basket")
def by_hour_plot_view(request):
    baskets = list(Basket.objects.priced().order_by("created_at"))
    context = {
        "plots": [by_hour_plot(baskets)],
    }
    return render(request, "purchase/snippets/plots.html", context)


@permission_required("purchase.view_basket")
def reports(request):
    template_name = "purchase/reports.html"
    baskets = list(Basket.objects.priced().order_by("created_at"))
    if not baskets:
        messages.warning(request, _("No sale to report"))
        return TemplateResponse(request, template_name, {})

    dates = Basket.objects.values_list("created_at__date", flat=True).distinct()
    average_basket_by_day = {
        date: Basket.objects.by_date(date).average_basket() for date in dates
    }
    turnover_by_day = {date: Basket.objects.by_date(date).turnover() for date in dates}

    products = Product.objects.with_turnover().with_sold()

    context = {
        "turnover": Basket.objects.turnover(),
        "turnover_by_day": turnover_by_day,
        "average_basket": Basket.objects.average_basket(),
        "average_basket_by_day": average_basket_by_day,
        "products": products,
        "payment_methods": PaymentMethod.objects.with_turnover().with_sold(),
        "no_payment_method": Basket.objects.no_payment_method().priced(),
    }
    return TemplateResponse(request, template_name, context)


def get_products_plots(products: ProductQuerySet):
    labels, sold, turnover = get_products_data_for_plot(products)

    x = np.arange(len(labels))
    width = 0.4
    fig: Figure = plt.figure()
    fig.suptitle(_("Sales by product"))

    color = "tab:orange"
    ax1: Axes = fig.add_subplot()
    bar: BarContainer = ax1.bar(x - width / 2, sold, width=width, color=color)
    ax1.bar_label(bar)
    ax1.tick_params(axis="x", rotation=15)
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_xticks(x, labels)
    ax1.set_ylabel(_("# sold"), color=color)

    color = "tab:blue"
    ax2: Axes = ax1.twinx()
    bar = ax2.bar(x + width / 2, turnover, width=width, color=color)
    ax2.bar_label(bar, fmt="%d€")
    ax2.set_ylabel(_("Turnover by product"), color=color)
    ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f€"))
    ax2.tick_params(axis="y", labelcolor=color)

    fig.tight_layout()
    img1 = get_image_from_fig(fig)

    fig = plt.figure()
    fig.suptitle(_("# sold"))
    ax1 = fig.add_subplot()
    ax1.pie(sold, labels=labels, autopct="%d%%")
    fig.tight_layout()
    img2 = get_image_from_fig(fig)

    fig = plt.figure()
    fig.suptitle(_("Turnover by product"))
    ax1 = fig.add_subplot()
    ax1.pie(turnover, labels=labels, autopct="%d%%")
    fig.tight_layout()
    img3 = get_image_from_fig(fig)

    return img1, img2, img3


def get_products_data_for_plot(products):
    labels = []
    sold = []
    turnover = []
    for product in products:
        labels.append(product.name)
        sold.append(product.sold)
        turnover.append(product.turnover / 100)
    return labels, sold, turnover


def by_hour_plot(baskets):
    labels, counts, turnovers = get_by_hour_data_for_plot(baskets)
    hours_in_day = 24
    fig: Figure = plt.figure()
    fig.suptitle(_("Sales by hour"))
    ax1: Axes = fig.add_subplot()

    color = "tab:orange"
    ax1.bar(labels, counts, width=1 / hours_in_day, color=color)
    ax1.tick_params(axis="x", rotation=15)
    ax1.xaxis.set_minor_locator(HourLocator())
    tz = ZoneInfo(settings.TIME_ZONE)
    locator = AutoDateLocator(tz=tz)
    ax1.xaxis.set_major_locator(locator)
    ax1.xaxis.set_major_formatter(ConciseDateFormatter(locator, tz=tz))
    ax1.set_ylabel(_("Basket count by hour"), color=color)
    ax1.set_yticks(np.linspace(*ax1.get_ybound(), 8))
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.grid(visible=True, which="major", axis="y")

    color = "tab:blue"
    ax2: Axes = ax1.twinx()
    ax2.plot(labels, turnovers, ".-", color=color)
    ax2.set_ylabel(_("Turnover by hour"), color=color)
    ax2.set_ylim(bottom=0)
    ax2.set_yticks(np.linspace(*ax2.get_ybound(), 8))
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f€"))

    fig.tight_layout()
    return get_image_from_fig(fig)


def get_by_hour_data_for_plot(baskets):
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
        labels.append(current.astimezone(ZoneInfo(settings.TIME_ZONE)))
        counts.append(count)
        turnovers.append(turnover)
        current = end_slot
    return labels, counts, turnovers


def get_image_from_fig(fig):
    image_data = StringIO()
    fig.savefig(image_data, format="svg")
    image_data.seek(0)
    img1 = image_data.getvalue()
    return img1
