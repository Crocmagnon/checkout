from django.urls import path

from common.views import home, ping

app_name = "common"
urlpatterns = [
    path("ping/", ping, name="ping"),
    path("", home, name="home"),
]
