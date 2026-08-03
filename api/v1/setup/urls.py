"""Rotas da API v1 do app setup."""

from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health_check, name="setup-health"),
]
