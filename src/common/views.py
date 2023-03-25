from django.shortcuts import redirect, render


def home(_request):
    return redirect("purchase:new")


def ping(request):
    return render(request, "common/ping.html", {})
