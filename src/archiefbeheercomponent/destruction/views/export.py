import io
import os
import zipfile
from typing import List
from uuid import uuid4
from wsgiref.util import FileWrapper

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    StreamingHttpResponse,
)
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DetailView

import xlsxwriter
from zgw_consumers.concurrent import parallel

from archiefbeheercomponent.accounts.models import User
from archiefbeheercomponent.constants import RoleTypeChoices

from ..forms import ZakenUrlsForm
from ..models import ArchiveConfig, DestructionList
from ..service import fetch_zaken
from ..utils import format_zaak_record, get_additional_zaak_info


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
            worksheet.write_row(
                row_count + 1, 0, format_zaak_record(zaak, user),
            )

        workbook.close()
        output.seek(0)

        return output.read()


class DownloadAdditionalReviewersDocumentsView(UserPassesTestMixin, DetailView):
    """
    Download a file uploaded by a reviewer during review
    """

    model = DestructionList

    def test_func(self):
        config = ArchiveConfig.get_solo()
        if not config.destruction_report_downloadable:
            return False

        user = self.request.user
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        destruction_list = self.get_object()
        if (
            destruction_list.assignees.filter(
                assignee=user, assignee__role__type=RoleTypeChoices.process_owner
            ).exists()
            or user.role.type == RoleTypeChoices.functional_admin
        ):
            return True

        return False

    def get(self, request, *args, **kwargs):
        destruction_list = get_object_or_404(DestructionList.objects, pk=kwargs["pk"])
        reviews = destruction_list.reviews.filter(~Q(additional_document__exact=""))

        if not reviews.count():
            raise Http404

        temp_file = io.BytesIO()
        with zipfile.ZipFile(temp_file, "w") as file:
            for review in reviews:
                filepath = review.additional_document.path
                file.write(filepath, arcname=os.path.basename(filepath))

        temp_file.seek(0)

        response = StreamingHttpResponse(
            FileWrapper(temp_file), content_type="application/zip",
        )

        response["Content-Disposition"] = "attachment;filename=reviewersDocuments.zip"
        return response
