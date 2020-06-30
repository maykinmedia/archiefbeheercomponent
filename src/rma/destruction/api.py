import itertools
from concurrent import futures

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.views import View

from rma.accounts.mixins import RoleRequiredMixin

from .models import ArchiveConfig, DestructionList
from .service import (
    fetch_zaak,
    get_besluiten,
    get_documenten,
    get_resultaat,
    get_zaaktypen,
    get_zaken,
)


class FetchZakenView(LoginRequiredMixin, View):
    def get(self, request):
        config = ArchiveConfig.get_solo()
        current_date = config.archive_date or timezone.now().date()
        #  default params for archived zaken
        query = {
            "archiefnominatie": "vernietigen",
            "archiefactiedatum__lt": current_date.isoformat(),
        }

        startdatum = request.GET.get("startdatum")
        zaaktypen = request.GET.get("zaaktypen")

        if startdatum:
            query["startdatum__gte"] = startdatum

        if zaaktypen:
            zaaktypen = zaaktypen.split(",")
            queries = [dict(query, **{"zaaktype": zaaktype}) for zaaktype in zaaktypen]
            # TODO: async
            with futures.ThreadPoolExecutor() as executor:
                zaken = list(executor.map(get_zaken, queries))

            # flat the list
            zaken = list(itertools.chain(*zaken))

        else:
            zaken = get_zaken(query_params=query)

        return JsonResponse({"zaken": zaken})


class FetchListItemsView(LoginRequiredMixin, View):
    def get(self, request, list_id):
        destruction_list = DestructionList.objects.get(id=list_id)

        fetched_zaaktypen = {zaaktype["url"]: zaaktype for zaaktype in get_zaaktypen()}

        zaak_urls = [item.zaak for item in destruction_list.items.all()]
        with futures.ThreadPoolExecutor() as executor:
            zaken = list(executor.map(fetch_zaak, zaak_urls))

        zaken = {zaak["url"]: zaak for zaak in zaken}

        # TODO: what to do with removed items?
        items = []
        for item in destruction_list.items.order_by("id").all():
            zaak = zaken[item.zaak]
            zaak["zaaktype"] = fetched_zaaktypen[zaak["zaaktype"]]
            items.append({"list_item_id": item.id, "zaak": zaak})

        return JsonResponse({"items": items})


class FetchZaakDetail(RoleRequiredMixin, View):
    role_permission = "can_view_case_details"

    def get(self, request):
        zaak_url = request.GET.get("zaak_url")
        if not zaak_url:
            return HttpResponseBadRequest("zaak_url query parameter must be specified")

        with futures.ThreadPoolExecutor() as executor:
            resultaat = executor.submit(get_resultaat, zaak_url)
            documenten = executor.submit(get_documenten, zaak_url)
            besluiten = executor.submit(get_besluiten, zaak_url)

        result = {
            "resultaat": resultaat.result(),
            "documenten": documenten.result(),
            "besluiten": besluiten.result(),
        }

        return JsonResponse(result)
