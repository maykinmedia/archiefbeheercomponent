from django.contrib import admin

from archiefvernietigingscomponent.emails.models import AutomaticEmail, EmailPreference


@admin.register(AutomaticEmail)
class AutomaticEmailAdmin(admin.ModelAdmin):
    list_display = ("type",)
    list_filter = ("type",)
    search_fields = ("type",)

    fields = ("type", "subject", "body")


@admin.register(EmailPreference)
class EmailPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "preference")
    list_filter = ("user",)
    search_fields = ("user",)

    fields = ("user", "preference")
