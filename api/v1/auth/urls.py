"""Rotas de autenticação JWT."""

from django.urls import path

from api.v1.auth import views

urlpatterns = [
    path("auth/login/", views.login, name="auth-login"),
    path("auth/refresh/", views.refresh, name="auth-refresh"),
    path("auth/logout/", views.logout, name="auth-logout"),
    path(
        "auth/switch-organization/",
        views.switch_organization,
        name="auth-switch-organization",
    ),
]
