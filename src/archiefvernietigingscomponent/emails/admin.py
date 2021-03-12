from django.contrib import admin

from archiefvernietigingscomponent.emails.models import AutomaticEmail


@admin.register(AutomaticEmail)
class AutomaticEmailAdmin(admin.ModelAdmin):
    list_display = ("type",)
    list_filter = ("type",)
    search_fields = ("type",)

    fields = ("type", "subject", "body")
