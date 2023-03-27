import logging

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import condition, require_http_methods
from django_htmx.http import trigger_client_event

from purchase.forms import PRICED_PREFIX, UNPRICED_PREFIX, BasketForm
from purchase.models import Basket, Product, reports_etag, reports_last_modified

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
@permission_required("purchase.add_basket")
def new_basket(request: WSGIRequest) -> HttpResponse:
    if request.method == "POST":
        form = BasketForm(request.POST)
        if form.is_valid():
            basket = form.save()
            update_with_unpriced_products(basket, request.POST)
            if request.user.has_perm("purchase.change_basket"):
                url = basket.get_absolute_url()
            else:
                url = reverse("purchase:new")
            messages.success(request, _("Successfully created basket."))
            return redirect(url)
    else:
        form = BasketForm()

    return TemplateResponse(
        request,
        "purchase/basket_form.html",
        {"form": form, "products": Product.objects.with_no_fixed_price()},
    )


def update_with_unpriced_products(basket: Basket, post_data: MultiValueDict):
    no_fixed_price = {
        product.id: product for product in Product.objects.with_no_fixed_price()
    }
    basket.items.filter(product__in=no_fixed_price.values()).delete()
    for product_id, product in no_fixed_price.items():
        if prices := post_data.getlist(f"{UNPRICED_PREFIX}{product_id}"):
            for price in map(int, prices):
                if price:
                    basket.items.create(
                        product=product,
                        quantity=1,
                        unit_price_cents=price,
                    )


@require_http_methods(["GET", "POST"])
@permission_required("purchase.change_basket")
def update_basket(request: WSGIRequest, pk: int) -> HttpResponse:
    basket = get_object_or_404(Basket.objects.priced(), pk=pk)
    if request.method == "POST":
        form = BasketForm(request.POST, instance=basket)
        if form.is_valid():
            basket = form.save()
            update_with_unpriced_products(basket, request.POST)
            messages.success(request, _("Successfully updated basket."))
            return redirect(basket.get_absolute_url())
    else:
        form = BasketForm(instance=basket)

    response = render(
        request,
        "purchase/basket_form.html",
        {
            "form": form,
            "basket": basket,
            "products": Product.objects.with_no_fixed_price(),
        },
    )
    trigger_client_event(response, "load-unpriced", after="swap")
    return response


@require_http_methods(["GET"])
def additional_unpriced_product(request: WSGIRequest) -> HttpResponse:
    product_id = request.GET.get("product_to_add")
    value = request.GET.get("value", 0)
    product = get_object_or_404(Product.objects.with_no_fixed_price(), pk=product_id)
    context = {"product": product, "value": value}
    return render(
        request,
        "purchase/snippets/basket_unpriced_item.html",
        context,
    )


@permission_required("purchase.view_basket")
@condition(etag_func=reports_etag, last_modified_func=reports_last_modified)
def list_baskets(request: WSGIRequest) -> HttpResponse:
    context = {"baskets": Basket.objects.priced().order_by("-id")}
    return TemplateResponse(request, "purchase/basket_list.html", context)


@require_http_methods(["GET", "POST"])
@permission_required("purchase.delete_basket")
def delete_basket(request: WSGIRequest, pk: int) -> HttpResponse:
    basket = get_object_or_404(Basket, pk=pk)
    if request.method == "GET":
        context = {"basket": basket}
        return TemplateResponse(request, "purchase/basket_confirm_delete.html", context)
    basket.delete()
    messages.success(request, _("Basket successfully deleted."))
    return redirect("purchase:list")


@require_http_methods(["POST"])
@permission_required("purchase.add_basket")
def price_preview(request: WSGIRequest) -> HttpResponse:
    total = 0
    for name in request.POST:
        if name.startswith(PRICED_PREFIX):
            product_id = name[len(PRICED_PREFIX) :]
            product = get_object_or_404(Product, pk=product_id)
            total += product.unit_price_cents * int(request.POST.get(name, 0))
        elif name.startswith(UNPRICED_PREFIX):
            total += sum(map(int, request.POST.getlist(name)))

    return HttpResponse(f"Montant total : {total/100:.2f}€")
