from django.urls import path

from transfers import api_views
from . import views

app_name = "transfers"

urlpatterns = [
    path("", views.home, name="home"),
    path("d/<str:token>/", views.download, name="download"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("api/upload/init/", api_views.upload_init, name="upload_init"),
    path("api/upload/complete/", api_views.upload_complete, name="upload_complete"),
]