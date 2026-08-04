"""Admin somente leitura do AuditLog."""

from django.contrib import admin

from core.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "action",
        "entity_type",
        "entity_id",
        "actor",
        "organization",
    )
    list_filter = ("action", "entity_type")
    search_fields = ("entity_id", "actor__email")
    readonly_fields = (
        "id",
        "actor",
        "action",
        "entity_type",
        "entity_id",
        "organization",
        "changes",
        "created_at",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
