"""URLs da API v1."""

from django.urls import include, path

urlpatterns = [
    path("", include("api.v1.health.urls")),
    path("", include("api.v1.me.urls")),
]
