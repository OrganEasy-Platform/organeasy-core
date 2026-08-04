"""Admin de usuários com auditoria."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from core.audit import build_model_diff, record_audit
from core.models import AuditLog
from users.models import User

USER_AUDIT_FIELDS = ["email", "full_name", "status", "is_staff", "is_superuser", "is_active"]


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "full_name", "status", "is_staff", "is_active", "date_joined")
    list_filter = ("status", "is_staff", "is_superuser", "is_active")
    search_fields = ("email", "full_name")
    readonly_fields = ("id", "date_joined", "last_login", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        (_("Perfil"), {"fields": ("full_name", "status")}),
        (
            _("Permissões"),
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (_("Datas"), {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "password1", "password2", "status", "is_staff"),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions")

    def save_model(self, request, obj, form, change) -> None:
        old = User.objects.filter(pk=obj.pk).first() if change else None
        super().save_model(request, obj, form, change)
        changes = build_model_diff(old, obj, USER_AUDIT_FIELDS)
        if not changes:
            return
        action = AuditLog.Action.CREATE if not change else AuditLog.Action.UPDATE
        if old is not None and old.status != obj.status:
            action = AuditLog.Action.STATUS_CHANGE
        record_audit(
            actor=request.user,
            action=action,
            entity_type=AuditLog.EntityType.USER,
            entity_id=obj.id,
            changes=changes,
        )
