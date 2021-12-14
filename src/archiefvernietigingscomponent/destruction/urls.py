from django.urls import include, path

from .api import FetchListItemsView, FetchZaakDetail, FetchZakenView
from .views import (
    DestructionListCreateView,
    DestructionListDetailView,
    DestructionListRedirectView,
    RecordManagerDestructionListView,
    ReviewCreateView,
    ReviewerDestructionListView,
    ZakenWithoutArchiveDateView,
)

app_name = "destruction"

urlpatterns = [
    path(
        "lijsten/",
        RecordManagerDestructionListView.as_view(),
        name="record-manager-list",
    ),
    path(
        "lijsten/toevoegen",
        DestructionListCreateView.as_view(),
        name="record-manager-create",
    ),
    path(
        "lijsten/<int:pk>/",
        DestructionListDetailView.as_view(),
        name="record-manager-detail",
    ),
    path(
        "lijsten/zaken-zonder-archiedactiedatum/",
        ZakenWithoutArchiveDateView.as_view(),
        name="zaken-without-archive-date",
    ),
    path("reviews/", ReviewerDestructionListView.as_view(), name="reviewer-list"),
    path(
        "reviews/<int:destruction_list>/toevoegen",
        ReviewCreateView.as_view(),
        name="reviewer-create",
    ),
    path("lijst/<int:pk>/", DestructionListRedirectView.as_view(), name="dl-redirect"),
    path(
        "_",
        include(
            [
                path("fetch-zaken", FetchZakenView.as_view(), name="fetch-zaken",),
                path(
                    "fetch-list-items/<int:list_id>",
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
