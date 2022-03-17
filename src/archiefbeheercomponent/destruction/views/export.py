import io
from typing import List
from uuid import uuid4

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.translation import gettext as _
from django.views import View

import xlsxwriter
from zgw_consumers.concurrent import parallel

from ...accounts.models import User
from ...report.utils import get_looptijd
from ..forms import ZakenUrlsForm
from ..service import fetch_zaken
from ..utils import get_additional_zaak_info


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

        with parallel() as executor:
            zaken_with_extra_info = list(executor.map(get_additional_zaak_info, zaken))

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
                _("Duration"),
                _("Organisation responsible"),
                _("Result type"),
                _("Retention period"),
                _("Destruction category selection list"),
                _("Relations"),
                _("Requesting user"),
            ],
        )

        for row_count, zaak in enumerate(zaken_with_extra_info):
            relations = _("No")
            if len(zaak.get("relevanteAndereZaken", [])):
                relations = _("Yes")

            worksheet.write_row(
                row_count + 1,
                0,
                [
                    zaak.get("identificatie"),
                    zaak["zaaktype"]["omschrijving"],
                    zaak.get("omschrijving"),
                    _("%(duration)s days") % {"duration": get_looptijd(zaak)},
                    zaak["verantwoordelijkeOrganisatie"],
                    zaak.get("resultaat", {})
                    .get("resultaattype", {})
                    .get("omschrijving")
                    or "",
                    zaak.get("resultaat", {})
                    .get("resultaattype", {})
                    .get("archiefactietermijn")
                    or "",
                    zaak["zaaktype"].get("processtype", {}).get("nummer") or "",
                    relations,
                    user_representation,
                ],
            )

        workbook.close()
        output.seek(0)

        return output.read()
