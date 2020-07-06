from django.urls import include, path

from .api import FetchListItemsView, FetchZaakDetail, FetchZakenView
from .views import (
    DestructionListCreateView,
    DestructionListDetailView,
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
    path(
        "record-managers/<pk>",
        DestructionListDetailView.as_view(),
        name="record-manager-detail",
    ),
    path("reviews/", ReviewerDestructionListView.as_view(), name="reviewer-list"),
    path(
        "reviews/<destruction_list>/add",
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
                path(
                    "fetch-zaak-detail",
                    FetchZaakDetail.as_view(),
                    name="fetch-zaak-detail",
                ),
            ]
        ),
    ),
]
