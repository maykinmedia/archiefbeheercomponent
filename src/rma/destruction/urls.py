from django.urls import include, path

from .api import FetchZakenView
from .views import (
    DestructionListCreateView,
    RecordManagerDestructionListView,
    ReviewerDestructionListView,
)

app_name = "destruction"

urlpatterns = [
    path(
        "record-managers/",
        RecordManagerDestructionListView.as_view(),
        name="record-manager-list",
    ),
    path(
        "record-managers/add",
        DestructionListCreateView.as_view(),
        name="record-manager-create",
    ),
    path("reviewers/", ReviewerDestructionListView.as_view(), name="reviewer-list",),
    path(
        "_",
        include([path("fetch-zaken", FetchZakenView.as_view(), name="fetch-zaken",),]),
    ),
]
