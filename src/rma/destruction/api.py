from datetime import date

from django.http import JsonResponse
from django.utils import timezone
from django.views import View

from .service import get_zaken


class FetchZakenView(View):
    def get(self, request):
        # today = timezone.now().date()
        # fixme replace with correct logic after creating test zaken
        today = date(year=2021, month=1, day=1)
        query = {"archiefnominatie": "vernietigen", "archiefactiedatum__lt": today}
        zaken = get_zaken(query_params=query)
        return JsonResponse({"zaken": zaken})
