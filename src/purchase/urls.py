from django.urls import path

from purchase.views import (
    DeleteBasketView,
    ListBasketsView,
    NewBasketView,
    UpdateBasketView,
)
from purchase.views.reports import ReportsView

app_name = "purchase"
urlpatterns = [
    path("", ListBasketsView.as_view(), name="list"),
    path("new/", NewBasketView.as_view(), name="new"),
    path("<int:pk>/update/", UpdateBasketView.as_view(), name="update"),
    path("<int:pk>/delete/", DeleteBasketView.as_view(), name="delete"),
    path("reports/", ReportsView.as_view(), name="reports"),
]