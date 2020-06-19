import itertools
from concurrent import futures

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from django.views import View

from .models import ArchiveConfig
from .service import get_zaken


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
