from django.contrib import admin

from privates.widgets import PrivateFileWidget

from archiefvernietigingscomponent.report.models import DestructionReport
from archiefvernietigingscomponent.report.views import DownloadDestructionReportView


@admin.register(DestructionReport)
class DestructionReportAdmin(admin.ModelAdmin):
    list_display = ("title", "process_owner")
    list_filter = ("title", "process_owner")
    search_fields = ("title", "process_owner")

    private_media_fields = ("content",)
    private_media_view_class = DownloadDestructionReportView
    private_media_file_widget = PrivateFileWidget

    # TODO filter users to attach to the report
