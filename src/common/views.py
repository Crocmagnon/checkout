from django.shortcuts import redirect, render


def home(_request):
    return redirect("purchase:new")


def ping(request):
    return render(request, "common/ping.html", {})


def error_check(_request):
    msg = "Error check"
    raise ValueError(msg)
