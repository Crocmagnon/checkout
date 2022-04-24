from django.urls import path

from purchase.views import NewBasketView, UpdateBasketView

app_name = "purchase"
urlpatterns = [
    path("new/", NewBasketView.as_view(), name="new"),
    path("update/<int:pk>/", UpdateBasketView.as_view(), name="update"),
]
