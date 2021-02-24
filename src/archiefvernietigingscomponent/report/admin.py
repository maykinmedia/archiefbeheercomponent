from django.contrib import admin

from privates.widgets import PrivateFileWidget

from archiefvernietigingscomponent.report.models import DestructionReport
from archiefvernietigingscomponent.report.views import DownloadDestructionReportView


@admin.register(DestructionReport)
class DestructionReportAdmin(admin.ModelAdmin):
    list_display = ("title", "destruction_list", "process_owner")
    list_filter = ("title", "destruction_list", "process_owner")
    search_fields = ("title", "destruction_list", "process_owner")

    private_media_fields = ("content",)
    private_media_view_class = DownloadDestructionReportView
    private_media_file_widget = PrivateFileWidget

    readonly_fields = ("title", "content", "destruction_list", "process_owner")
