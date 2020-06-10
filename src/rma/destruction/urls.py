from django.urls import path

from .views import RecordManagerDestructionListView

app_name = "destruction"

urlpatterns = [
    path(
        "record-managers/",
        RecordManagerDestructionListView.as_view(),
        name="record-manager-list",
    ),
]
