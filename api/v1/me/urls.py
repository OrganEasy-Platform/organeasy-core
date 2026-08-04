"""Rotas do perfil autenticado."""

from django.urls import path

from api.v1.me import views

urlpatterns = [
    path("me/", views.me, name="me"),
    path("me/organizations/", views.my_organizations, name="my-organizations"),
]
