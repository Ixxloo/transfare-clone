from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "transfers"

urlpatterns = [
    path("", views.home, name="home"),
    path("d/<str:token>/", views.download, name="download"),
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # New Account & Auth routes
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_type_or_template if hasattr(auth_views, 'LoginView') else auth_views.LoginView.as_view(template_name="transfers/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="transfers:home"), name="logout"),
]