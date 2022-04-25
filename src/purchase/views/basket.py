from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from purchase.forms import BasketForm
from purchase.models import Basket
from purchase.views.utils import ProtectedViewsMixin


class NewBasketView(ProtectedViewsMixin, SuccessMessageMixin, CreateView):
    permission_required = ["purchase.add_basket"]
    model = Basket
    form_class = BasketForm
    success_message = "Successfully created basket."

    queryset = Basket.objects.priced()

    def get_success_url(self):
        if self.request.user.has_perm("purchase.change_basket"):
            return super().get_success_url()
        else:
            return reverse("purchase:new")


class UpdateBasketView(ProtectedViewsMixin, SuccessMessageMixin, UpdateView):
    permission_required = ["purchase.change_basket", "purchase.view_basket"]
    model = Basket
    form_class = BasketForm
    success_message = "Successfully updated basket."
    queryset = Basket.objects.priced()


class ListBasketsView(ProtectedViewsMixin, ListView):
    permission_required = ["purchase.view_basket"]
    model = Basket
    context_object_name = "baskets"
    ordering = "-id"
    queryset = Basket.objects.priced()


class DeleteBasketView(ProtectedViewsMixin, SuccessMessageMixin, DeleteView):
    permission_required = ["purchase.delete_basket"]
    model = Basket
    success_message = "Basket successfully deleted."
    queryset = Basket.objects.priced()

    def get_success_url(self):
        return reverse("purchase:list")
