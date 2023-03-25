from django.urls import path

from common import views

app_name = "common"
urlpatterns = [
    path("error_check/", views.error_check, name="error_check"),
    path("ping/", views.ping, name="ping"),
    path("", views.home, name="home"),
]
