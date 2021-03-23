from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from privates.admin import PrivateMediaMixin

from archiefvernietigingscomponent.report.models import DestructionReport


@admin.register(DestructionReport)
class DestructionReportAdmin(PrivateMediaMixin, admin.ModelAdmin):
    list_display = ("title", "destruction_list", "process_owner")
    list_filter = ("title", "destruction_list", "process_owner")
    search_fields = ("title", "destruction_list", "process_owner")
    readonly_fields = ("title", "destruction_list", "process_owner", "file_content")

    private_media_fields = ("content",)

    exclude = ("content",)

    def file_content(self, instance):
        url = reverse("admin:report_destructionreport_content", args=[instance.pk])
        filename = instance.content.name.split("/")[-1]
        return format_html('<a href="%s">%s</a>' % (url, filename))

    def has_add_permission(self, request, obj=None):
        return False
