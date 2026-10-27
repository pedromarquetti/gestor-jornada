from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import RedirectView, TemplateView


class LogoutView(TemplateView):
    """Custom logout page that redirects to / or /login."""

    template_name = "logout.html"

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return redirect("home")


class LoginForm(AuthenticationForm):
    """
    Custom login form that redirects to the home page after a successful login.
    """

    def login(self, request, user):
        """
        Overrides the default login method to redirect to the home page.
        """
        super().login(request, user)
        self.next_url = request.POST.get("next", reverse_lazy("home"))
        return RedirectView.as_view(url=self.next_url, permanent=False)


class HomeView(LoginRequiredMixin, TemplateView):
    """
    Protected home page that displays the authenticated user's information.
    """

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context
