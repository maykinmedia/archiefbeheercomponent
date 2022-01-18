from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from zgw_consumers.concurrent import parallel

from archiefbeheercomponent.accounts.mixins import (
    AuthorOrAssigneeRequiredMixin,
    RoleRequiredMixin,
)

from ..constants import RoleTypeChoices
from .constants import ListItemStatus
from .models import ArchiveConfig, DestructionList
from .service import (
    fetch_zaak,
    get_besluiten,
    get_documenten,
    get_resultaat,
    get_zaaktypen,
    get_zaken,
)
from .utils import (
    get_additional_zaak_info,
    get_zaak_link_for_zaakafhandelcomponent,
    set_zaken_availability,
)


class FetchZakenView(LoginRequiredMixin, View):
    def get(self, request):
        zaken = get_zaken(request.GET)

        with parallel() as executor:
            zaken_with_extra_info = list(executor.map(get_additional_zaak_info, zaken))

        set_zaken_availability(zaken_with_extra_info)

        return JsonResponse({"zaken": zaken_with_extra_info})


NO_DETAIL_ZAAK_ATTRS = [
    "url",
    "identificatie",
    "archiefnominatie",
    "archiefactiedatum",
    "relevanteAndereZaken",
    "verantwoordelijkeOrganisatie",
    "toelichting",
    "resultaat",
    "startdatum",
    "einddatum",
]
NO_DETAIL_ZAAKTYPE_ATTRS = [
    "url",
    "omschrijving",
    "versiedatum",
    "selectielijstProcestype",
]


class FetchListItemsView(AuthorOrAssigneeRequiredMixin, View):
    def get_destruction_list(self):
        return get_object_or_404(DestructionList, id=self.kwargs["list_id"])

    def get(self, request, list_id):
        config = ArchiveConfig.get_solo()

        destruction_list = DestructionList.objects.get(id=list_id)
        last_review = destruction_list.last_review()

        fetched_zaaktypen = {zaaktype["url"]: zaaktype for zaaktype in get_zaaktypen()}

        zaak_urls = [item.zaak for item in destruction_list.items.all()]
        with parallel() as executor:
            zaken = list(executor.map(fetch_zaak, zaak_urls))

        zaken = {zaak["url"]: zaak for zaak in zaken}

        items = []
        for item in (
            destruction_list.items.exclude(status=ListItemStatus.removed)
            .order_by("id")
            .all()
        ):
            # list item data
            list_item_data = {"id": item.id, "status": item.status}
            if (
                last_review
                and last_review.item_reviews.filter(destruction_list_item=item).exists()
            ):
                item_review = last_review.item_reviews.get(destruction_list_item=item)
                list_item_data.update(
                    {
                        "review_text": item_review.text,
                        "review_suggestion": item_review.suggestion,
                    }
                )

            # full zaak data
            zaak = zaken[item.zaak]
            zaaktype = fetched_zaaktypen[zaak["zaaktype"]]

            # return only general information
            zaak_data = {attr: zaak.get(attr) for attr in NO_DETAIL_ZAAK_ATTRS}
            # Add link to zaak in ZAC
            zaak_data["zac_link"] = get_zaak_link_for_zaakafhandelcomponent(
                zaak, config.link_to_zac
            )

            zaaktype_data = {
                attr: zaaktype.get(attr) for attr in NO_DETAIL_ZAAKTYPE_ATTRS
            }
            zaak_data["zaaktype"] = zaaktype_data
            zaak_data = get_additional_zaak_info(zaak_data)

            if (
                not destruction_list.contains_sensitive_info
                or self.request.user.role.type != RoleTypeChoices.archivist
            ):
                zaak_data["omschrijving"] = zaak.get("omschrijving")

            items.append({"listItem": list_item_data, "zaak": zaak_data})

        return JsonResponse({"items": items})


class FetchZaakDetail(RoleRequiredMixin, View):
    role_permission = "can_view_case_details"

    def get(self, request):
        zaak_url = request.GET.get("zaak_url")
        if not zaak_url:
            return HttpResponseBadRequest("zaak_url query parameter must be specified")

        with parallel() as executor:
            resultaat = executor.submit(get_resultaat, zaak_url)
            documenten = executor.submit(get_documenten, zaak_url)
            besluiten = executor.submit(get_besluiten, zaak_url)

        result = {
            "resultaat": resultaat.result(),
            "documenten": documenten.result(),
            "besluiten": besluiten.result(),
        }

        return JsonResponse(result)
