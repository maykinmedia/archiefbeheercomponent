import io
from typing import List
from uuid import uuid4

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.translation import gettext as _
from django.views import View

import xlsxwriter

from ...accounts.models import User
from ..forms import ZakenUrlsForm
from ..service import fetch_zaken


class ExportZakenWithoutArchiveDateView(UserPassesTestMixin, View):
    form_class = ZakenUrlsForm

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if user.role.can_start_destruction:
            return True

        return False

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET)
        if not form.is_valid():
            return HttpResponseBadRequest(_("Invalid cases URLs"))

        zaken_urls = form.cleaned_data["zaken_urls"]
        data = self.get_data(zaken_urls, request.user)

        response = HttpResponse(
            data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        filename = f"zaken-lijst-{uuid4()}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response

    def get_data(self, zaken_urls: List[str], user: User):
        zaken = fetch_zaken(zaken_urls)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet(name=_("Cases without archive date"))

        user_representation = f"{user.first_name} {user.last_name}"

        # Header
        worksheet.write_row(
            0,
            0,
            [
                _("Case identification"),
                _("Case type"),
                _("Case description"),
                _("Requesting user"),
            ],
        )

        for row_count, zaak in enumerate(zaken):
            worksheet.write_row(
                row_count + 1,
                0,
                [
                    zaak.get("identificatie"),
                    zaak["zaaktype"]["omschrijving"],
                    zaak.get("omschrijving"),
                    user_representation,
                ],
            )

        workbook.close()
        output.seek(0)

        return output.read()
