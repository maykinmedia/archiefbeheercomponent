from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from hijack_admin.admin import HijackUserAdminMixin

from .models import Role, User


@admin.register(User)
class _UserAdmin(UserAdmin, HijackUserAdminMixin):
    list_display = UserAdmin.list_display + ("hijack_field",)


class UserInline(admin.TabularInline):
    model = User
    extra = 1


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "can_start_destruction",
        "can_review_destruction",
        "can_view_case_details",
    )
    inlines = [UserInline]
