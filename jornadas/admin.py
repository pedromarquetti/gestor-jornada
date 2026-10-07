from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Role, Task, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(User)
class JornadasUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": ("role",),
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "fields": ("role",),
            },
        ),
    )
    list_display = UserAdmin.list_display + ("role",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["activity", "user", "started_at", "ended_at"]
    list_filter = ["user", "started_at"]
    list_select_related = ["user"]
