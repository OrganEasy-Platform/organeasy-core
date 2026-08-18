"""Rotas de organizações (onboarding — Pacote B)."""

from django.urls import path

from api.v1.organizations import views

urlpatterns = [
    path("organizations/", views.organization_create, name="organization-create"),
    path(
        "organizations/join-by-code/",
        views.join_by_code,
        name="organization-join-by-code",
    ),
    path(
        "organizations/join-requests/<uuid:request_id>/cancel/",
        views.join_request_cancel,
        name="organization-join-request-cancel",
    ),
    path(
        "organizations/<uuid:organization_id>/join-requests/<uuid:request_id>/approve/",
        views.join_request_approve,
        name="organization-join-request-approve",
    ),
    path(
        "organizations/<uuid:organization_id>/join-requests/<uuid:request_id>/reject/",
        views.join_request_reject,
        name="organization-join-request-reject",
    ),
    path(
        "organizations/<uuid:organization_id>/join-requests/",
        views.join_requests,
        name="organization-join-requests",
    ),
    path(
        "organizations/<uuid:organization_id>/invite-codes/<uuid:invite_id>/deactivate/",
        views.invite_code_deactivate,
        name="organization-invite-code-deactivate",
    ),
    path(
        "organizations/<uuid:organization_id>/invite-codes/",
        views.invite_codes,
        name="organization-invite-codes",
    ),
]
