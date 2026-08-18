"""Admin de organizações, vínculos e auditoria embutida."""

from __future__ import annotations

from django.contrib import admin

from core.audit import build_model_diff, record_audit
from core.models import AuditLog
from organizations.models import (
    Organization,
    OrganizationInviteCode,
    OrganizationJoinRequest,
    OrganizationMembership,
)

ORG_AUDIT_FIELDS = ["name", "slug", "status", "created_by"]
MEMBERSHIP_AUDIT_FIELDS = ["status", "is_default"]


class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    autocomplete_fields = ("user",)
    readonly_fields = ("id", "joined_at", "created_at", "updated_at")
    fields = (
        "user",
        "status",
        "is_default",
        "joined_at",
        "id",
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "status", "created_by", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("created_by",)
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [OrganizationMembershipInline]

    def save_model(self, request, obj, form, change) -> None:
        old = Organization.objects.filter(pk=obj.pk).first() if change else None
        super().save_model(request, obj, form, change)
        changes = build_model_diff(old, obj, ORG_AUDIT_FIELDS)
        if not changes:
            return
        action = AuditLog.Action.CREATE if not change else AuditLog.Action.UPDATE
        if old is not None and old.status != obj.status:
            action = AuditLog.Action.STATUS_CHANGE
        record_audit(
            actor=request.user,
            action=action,
            entity_type=AuditLog.EntityType.ORGANIZATION,
            entity_id=obj.id,
            organization=obj,
            changes=changes,
        )

    def save_formset(self, request, form, formset, change) -> None:
        # Auditoria de memberships criados/alterados via inline da organização.
        instances = formset.save(commit=False)
        for obj in instances:
            # UUID PK já existe em memória antes do INSERT — checar no banco.
            old = OrganizationMembership.objects.filter(pk=obj.pk).first()
            obj.save()
            audit_fields = MEMBERSHIP_AUDIT_FIELDS
            if old is None:
                audit_fields = MEMBERSHIP_AUDIT_FIELDS + ["user_id", "organization_id"]
            changes = build_model_diff(old, obj, audit_fields)
            if not changes:
                continue
            action = AuditLog.Action.CREATE if old is None else AuditLog.Action.UPDATE
            if old is not None and old.status != obj.status:
                action = AuditLog.Action.STATUS_CHANGE
            record_audit(
                actor=request.user,
                action=action,
                entity_type=AuditLog.EntityType.MEMBERSHIP,
                entity_id=obj.id,
                organization=obj.organization,
                changes=changes,
            )
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "organization",
        "status",
        "is_default",
        "joined_at",
    )
    list_filter = ("status", "is_default")
    search_fields = ("user__email", "organization__name", "organization__slug")
    autocomplete_fields = ("user", "organization")
    readonly_fields = ("id", "joined_at", "created_at", "updated_at")

    def save_model(self, request, obj, form, change) -> None:
        old = (
            OrganizationMembership.objects.filter(pk=obj.pk).first() if change else None
        )
        super().save_model(request, obj, form, change)
        fields = MEMBERSHIP_AUDIT_FIELDS if change else MEMBERSHIP_AUDIT_FIELDS + [
            "user_id",
            "organization_id",
        ]
        changes = build_model_diff(old, obj, fields)
        if not changes:
            return
        action = AuditLog.Action.CREATE if not change else AuditLog.Action.UPDATE
        if old is not None and old.status != obj.status:
            action = AuditLog.Action.STATUS_CHANGE
        record_audit(
            actor=request.user,
            action=action,
            entity_type=AuditLog.EntityType.MEMBERSHIP,
            entity_id=obj.id,
            organization=obj.organization,
            changes=changes,
        )


@admin.register(OrganizationInviteCode)
class OrganizationInviteCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "organization",
        "is_active",
        "use_count",
        "max_uses",
        "expires_at",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("code", "organization__name", "organization__slug")
    autocomplete_fields = ("organization", "created_by")
    readonly_fields = ("id", "use_count", "created_at", "updated_at")


@admin.register(OrganizationJoinRequest)
class OrganizationJoinRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "organization",
        "status",
        "reviewed_by",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("user__email", "organization__name", "organization__slug")
    autocomplete_fields = ("user", "organization", "reviewed_by")
    readonly_fields = ("id", "created_at", "updated_at", "reviewed_at")
