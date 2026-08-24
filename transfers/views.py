from django.shortcuts import render

from django.shortcuts import render

def home(request):
    return render(request, "transfers/home.html")

def download(request, token):
    return render(request, "transfers/download.html", {"token": token})

def dashboard(request):
    return render(request, "transfers/dashboard.html")