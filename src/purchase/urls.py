from django.urls import path

from purchase.views import delete_basket, list_baskets, new_basket, update_basket
from purchase.views.reports import by_hour_plot_view, products_plots_view, reports

app_name = "purchase"
urlpatterns = [
    path("", list_baskets, name="list"),
    path("new/", new_basket, name="new"),
    path("<int:pk>/update/", update_basket, name="update"),
    path("<int:pk>/delete/", delete_basket, name="delete"),
    path("reports/", reports, name="reports"),
    # plots
    path("reports/products_plots/", products_plots_view, name="products_plots"),
    path("reports/by_hour_plot/", by_hour_plot_view, name="by_hour_plot"),
]
