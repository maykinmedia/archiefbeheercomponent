from django.conf import settings
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View

from requests import Request

from archiefbeheercomponent.accounts.models import User


class DemoLoginView(View):
    def get(self, request: Request, pk: int) -> HttpResponse:
        if not settings.ABC_DEMO_MODE:
            raise PermissionDenied

        demo_users = User.objects.filter(username__startswith="demo-")
        requested_user = demo_users.filter(pk=pk).first()

        if requested_user:
            login(
                request,
                requested_user,
                backend="django.contrib.auth.backends.ModelBackend",
            )

        return HttpResponseRedirect(redirect_to=reverse("entry"))
