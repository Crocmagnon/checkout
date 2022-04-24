from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

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
