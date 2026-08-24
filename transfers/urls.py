from django.urls import path
from . import views

app_name = "transfers"

urlpatterns = [
    path("", views.home, name="home"),
    path("d/<str:token>/", views.download, name="download"),
    path("dashboard/", views.dashboard, name="dashboard"),
]