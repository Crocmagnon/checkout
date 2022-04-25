from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from purchase.forms import BasketForm
from purchase.models import Basket


class ProtectedViewsMixin(PermissionRequiredMixin, LoginRequiredMixin):
    pass


class NewBasketView(ProtectedViewsMixin, CreateView):
    permission_required = ["purchase.add_basket"]
    model = Basket
    form_class = BasketForm


class UpdateBasketView(ProtectedViewsMixin, UpdateView):
    permission_required = ["purchase.change_basket", "purchase.view_basket"]
    model = Basket
    form_class = BasketForm


class ListBasketsView(ProtectedViewsMixin, ListView):
    permission_required = ["purchase.view_basket"]
    model = Basket
    context_object_name = "baskets"
    ordering = "-id"


class DeleteBasketView(ProtectedViewsMixin, DeleteView):
    permission_required = ["purchase.delete_basket"]
    model = Basket

    def get_success_url(self):
        return reverse("purchase:list")
