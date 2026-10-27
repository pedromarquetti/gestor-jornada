from django.contrib.auth.views import LoginView
from django.urls import path

from .views import HomeView, LogoutView

urlpatterns = [
    path(
        "login/", LoginView.as_view(template_name="login.html"), name="jornadas_login"
    ),
    path("logout/", LogoutView.as_view(), name="jornadas_logout"),
    path("", HomeView.as_view(), name="home"),
]
