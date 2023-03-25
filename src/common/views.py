from django.shortcuts import redirect


def home(_request):
    return redirect("purchase:new")
