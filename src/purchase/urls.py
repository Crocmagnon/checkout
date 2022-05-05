from django.urls import path

from purchase.views import delete_basket, list_baskets, new_basket, update_basket
from purchase.views.reports import reports

app_name = "purchase"
urlpatterns = [
    path("", list_baskets, name="list"),
    path("new/", new_basket, name="new"),
    path("<int:pk>/update/", update_basket, name="update"),
    path("<int:pk>/delete/", delete_basket, name="delete"),
    path("reports/", reports, name="reports"),
]
