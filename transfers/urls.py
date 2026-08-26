from django.urls import path

from transfers import api_views
from django.contrib.auth import views as auth_views
from . import views

app_name = "transfers"

urlpatterns = [
    path("", views.home, name="home"),
    path("d/<str:token>/", views.download, name="download"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("api/upload/init/", api_views.upload_init, name="upload_init"),
    path("api/upload/complete/", api_views.upload_complete, name="upload_complete"),
    
    # New Account & Auth routes
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="transfers/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="transfers:home"), name="logout"),
    path("d/<str:token>/f/<int:file_id>/", views.download_file, name="download_file"),
]