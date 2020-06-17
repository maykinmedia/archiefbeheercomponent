from datetime import date

from django.http import JsonResponse
from django.utils import timezone
from django.views import View

from .service import get_zaken


class FetchZakenView(View):
    def get(self, request):
        today = timezone.now().date()
        #  default params for archived zaken
        query = {"archiefnominatie": "vernietigen", "archiefactiedatum__lt": today}

        startdatum = request.GET.get("startdatum")
        zaaktypen = request.GET.get("zaaktypen")

        if startdatum:
            query["startdatum__gte"] = startdatum

        if zaaktypen:
            zaken = []
            zaaktypen = zaaktypen.split(",")
            for zaaktype in zaaktypen:
                query["zaaktype"] = zaaktype
                zaken += get_zaken(query_params=query)

        else:
            zaken = get_zaken(query_params=query)
        return JsonResponse({"zaken": zaken})
