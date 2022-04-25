from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from purchase.forms import BasketForm
from purchase.models import Basket


class ProtectedViewsMixin(PermissionRequiredMixin, LoginRequiredMixin):
    pass


class NewBasketView(ProtectedViewsMixin, SuccessMessageMixin, CreateView):
    permission_required = ["purchase.add_basket"]
    model = Basket
    form_class = BasketForm
    success_message = "Successfully created basket."


class UpdateBasketView(ProtectedViewsMixin, SuccessMessageMixin, UpdateView):
    permission_required = ["purchase.change_basket", "purchase.view_basket"]
    model = Basket
    form_class = BasketForm
    success_message = "Successfully updated basket."


class ListBasketsView(ProtectedViewsMixin, ListView):
    permission_required = ["purchase.view_basket"]
    model = Basket
    context_object_name = "baskets"
    ordering = "-id"


class DeleteBasketView(ProtectedViewsMixin, SuccessMessageMixin, DeleteView):
    permission_required = ["purchase.delete_basket"]
    model = Basket
    success_message = "Basket successfully deleted."

    def get_success_url(self):
        return reverse("purchase:list")
