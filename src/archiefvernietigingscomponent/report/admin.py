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

    private_media_fields = ("content_pdf", "content_csv")

    exclude = ("content",)

    def file_content(self, instance):
        extensions = ["pdf", "csv"]

        html_snippet = ""
        for extension in extensions:
            url = reverse(
                f"admin:report_destructionreport_content_{extension}",
                args=[instance.pk],
            )
            filename = getattr(instance, f"content_{extension}").name.split("/")[-1]
            html_snippet += '<div>%s: <a href="%s">%s</a></div>' % (
                extension,
                url,
                filename,
            )

        return format_html(html_snippet)

    def has_add_permission(self, request, obj=None):
        return False
