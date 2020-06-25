from django.urls import include, path

from .api import FetchListItemsView, FetchZakenView
from .views import (
    DestructionListCreateView,
    RecordManagerDestructionListView,
    ReviewCreateView,
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
    path("reviewers/", ReviewerDestructionListView.as_view(), name="reviewer-list"),
    path(
        "reviewers/<destruction_list>/add",
        ReviewCreateView.as_view(),
        name="reviewer-create",
    ),
    path(
        "_",
        include(
            [
                path("fetch-zaken", FetchZakenView.as_view(), name="fetch-zaken",),
                path(
                    "fetch-list-items/<list_id>",
                    FetchListItemsView.as_view(),
                    name="fetch-list-items",
                ),
            ]
        ),
    ),
]
