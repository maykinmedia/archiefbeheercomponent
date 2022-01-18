from django.contrib import admin

from solo.admin import SingletonModelAdmin

from archiefbeheercomponent.emails.forms import AutomaticEmailForm
from archiefbeheercomponent.emails.models import (
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


@admin.register(EmailConfig)
class EmailConfigsAdmin(SingletonModelAdmin):
    fields = ("municipality", "from_email")
