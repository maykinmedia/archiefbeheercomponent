from django.urls import path

from archiefbeheercomponent.report.views import DownloadDestructionReportView

app_name = "report"

urlpatterns = [
    path(
        "download/<int:pk>/",
        DownloadDestructionReportView.as_view(),
        name="download-report",
    ),
]
