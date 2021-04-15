from django.contrib import admin

from solo.admin import SingletonModelAdmin

from archiefvernietigingscomponent.emails.forms import (
    AutomaticEmailForm,
    EmailPreferenceAdminForm,
)
from archiefvernietigingscomponent.emails.models import (
    AutomaticEmail,
    EmailConfig,
    EmailPreference,
)


@admin.register(AutomaticEmail)
class AutomaticEmailAdmin(admin.ModelAdmin):
    list_display = ("type",)
    list_filter = ("type",)
    search_fields = ("type",)

    form = AutomaticEmailForm


@admin.register(EmailPreference)
class EmailPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "preference")
    list_filter = ("user",)
    search_fields = ("user",)

    fields = ("user", "preference")


class EmailPreferenceInline(admin.StackedInline):
    model = EmailPreference
    form = EmailPreferenceAdminForm

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EmailConfig)
class EmailConfigsAdmin(SingletonModelAdmin):
    fields = ("municipality", "from_email")
