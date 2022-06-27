from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from hijack.contrib.admin import HijackUserAdminMixin
from ordered_model.admin import OrderedModelAdmin

from .models import Role, User


@admin.register(User)
class _UserAdmin(HijackUserAdminMixin, UserAdmin):
    list_display = UserAdmin.list_display + ("role",)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        return tuple(fieldsets) + ((_("Role"), {"fields": ("role",)}),)


class UserInline(admin.TabularInline):
    model = User
    fields = UserAdmin.list_display

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Role)
class RoleAdmin(OrderedModelAdmin):
    list_display = (
        "name",
        "can_start_destruction",
        "can_review_destruction",
        "can_view_case_details",
        "move_up_down_links",
    )
    inlines = [UserInline]
