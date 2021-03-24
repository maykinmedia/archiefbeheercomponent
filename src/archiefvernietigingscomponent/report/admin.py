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
    readonly_fields = (
        "title",
        "destruction_list",
        "process_owner",
        "file_content_pdf",
        "file_content_csv",
    )

    private_media_fields = ("content_pdf", "content_csv")

    exclude = ("content_pdf", "content_csv")

    def get_report_html_link(self, instance, extension) -> str:
        url = reverse("report:download-report", args=[instance.pk],)
        url += f"?type={extension}"
        filename = getattr(instance, f"content_{extension}").name.split("/")[-1]
        return '<a href="%s">%s</a>' % (url, filename,)

    def file_content_pdf(self, instance):
        html_snippet = self.get_report_html_link(instance=instance, extension="pdf")
        return format_html(html_snippet)

    def file_content_csv(self, instance):
        html_snippet = self.get_report_html_link(instance=instance, extension="csv")
        return format_html(html_snippet)

    def has_add_permission(self, request, obj=None):
        return False
