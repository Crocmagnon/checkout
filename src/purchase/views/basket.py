from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import condition, require_http_methods

from purchase.forms import BasketForm
from purchase.models import Basket, reports_etag, reports_last_modified


@require_http_methods(["GET", "POST"])
@permission_required("purchase.add_basket")
def new_basket(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = BasketForm(request.POST)
        if form.is_valid():
            instance = form.save()
            if request.user.has_perm("purchase.change_basket"):
                url = instance.get_absolute_url()
            else:
                url = reverse("purchase:new")
            messages.success(request, _("Successfully created basket."))
            return redirect(url)
    else:
        form = BasketForm()

    return TemplateResponse(request, "purchase/basket_form.html", {"form": form})


@require_http_methods(["GET", "POST"])
@permission_required("purchase.change_basket")
def update_basket(request: HttpRequest, pk: int) -> HttpResponse:
    basket = get_object_or_404(Basket.objects.priced(), pk=pk)
    if request.method == "POST":
        form = BasketForm(request.POST, instance=basket)
        if form.is_valid():
            basket = form.save()
            messages.success(request, _("Successfully updated basket."))
            return redirect(basket.get_absolute_url())
    else:
        form = BasketForm(instance=basket)

    return TemplateResponse(
        request,
        "purchase/basket_form.html",
        {"form": form, "basket": basket},
    )


@permission_required("purchase.view_basket")
@condition(etag_func=reports_etag, last_modified_func=reports_last_modified)
def list_baskets(request: HttpRequest) -> HttpResponse:
    context = {"baskets": Basket.objects.priced().order_by("-id")}
    return TemplateResponse(request, "purchase/basket_list.html", context)


@require_http_methods(["GET", "POST"])
@permission_required("purchase.delete_basket")
def delete_basket(request: HttpRequest, pk: int) -> HttpResponse:
    basket = get_object_or_404(Basket, pk=pk)
    if request.method == "GET":
        context = {"basket": basket}
        return TemplateResponse(request, "purchase/basket_confirm_delete.html", context)
    basket.delete()
    messages.success(request, _("Basket successfully deleted."))
    return redirect("purchase:list")
