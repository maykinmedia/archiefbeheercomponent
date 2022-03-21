import csv
import io
from datetime import date, datetime
from itertools import chain
from typing import ByteString, List, Optional, Tuple

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.http import HttpRequest
from django.shortcuts import render
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext as _

from weasyprint import HTML
from zds_client import ClientError

from archiefbeheercomponent.constants import RoleTypeChoices
from archiefbeheercomponent.destruction.constants import ListItemStatus, ReviewStatus
from archiefbeheercomponent.destruction.models import (
    DestructionList,
    DestructionListReview,
)
from archiefbeheercomponent.destruction.service import (
    fetch_process_type,
    fetch_zaaktype,
)
from archiefbeheercomponent.report.models import DestructionReport


class NoClientException(Exception):
    """No client could be built"""

    pass


def get_looptijd(zaak: dict) -> int:

    if zaak.get("einddatum"):
        end_date = date.fromisoformat(zaak["einddatum"])
    else:
        end_date = date.today()

    return (end_date - date.fromisoformat(zaak["startdatum"])).days


def get_vernietigings_categorie_selectielijst(selectielijst_procestype: str) -> str:
    try:
        process_type = fetch_process_type(selectielijst_procestype)
    except ClientError:
        # If the process type couldn't be retrieved, return an empty value
        return ""

    return str(process_type["nummer"])


def get_destruction_list_archivaris_comments(destruction_list: DestructionList) -> str:
    review = (
        DestructionListReview.objects.filter(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author__role__type=RoleTypeChoices.archivist,
        )
        .order_by("created")
        .last()
    )

    if not review:
        return ""

    return review.text


def get_zaaktype(zaaktype_url: str) -> dict:
    try:
        return fetch_zaaktype(zaaktype_url)
    except ClientError:
        # If the zaaktype couldn't be retrieved, return an empty dictionary
        return {}


def get_process_owner_comments(destruction_list: DestructionList) -> str:
    review = (
        DestructionListReview.objects.filter(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author__role__type=RoleTypeChoices.process_owner,
        )
        .order_by("created")
        .last()
    )

    if not review:
        return ""

    return review.text


def get_destruction_report_data(
    destruction_list: DestructionList,
) -> Tuple[List[dict], int]:
    destroyed_items = destruction_list.items.filter(
        status=ListItemStatus.destroyed
    ).order_by("id")

    zaken_data = []
    bytes_deleted = 0
    for destroyed_item in destroyed_items:
        zaak_data = destroyed_item.extra_zaak_data
        bytes_deleted += zaak_data["bytes_removed_documents"]

        zaaktype = get_zaaktype(zaak_data["zaaktype"])

        if not destruction_list.contains_sensitive_info:
            zaak_data["opmerkingen"] = get_destruction_list_archivaris_comments(
                destruction_list
            )
        else:
            del zaak_data["omschrijving"]

        zaak_data["zaaktype"] = (
            zaaktype["omschrijving"] if "omschrijving" in zaaktype else ""
        )
        zaak_data["looptijd"] = _("%(looptijd)s days") % {
            "looptijd": get_looptijd(zaak_data)
        }
        zaak_data["vernietigings_categorie"] = (
            get_vernietigings_categorie_selectielijst(
                zaaktype["selectielijstProcestype"]
            )
            if zaaktype.get("selectielijstProcestype")
            else ""
        )
        zaak_data["reactie_zorgdrager"] = get_process_owner_comments(destruction_list)

        if zaak_data.get("resultaat"):
            resultaattype = zaak_data["resultaat"]["resultaattype"]
            zaak_data["resultaattype"] = resultaattype["omschrijving"]
            zaak_data["archiefactietermijn"] = (
                resultaattype["archiefactietermijn"]
                if resultaattype.get("archiefactietermijn")
                else ""
            )

        if len(zaak_data["relevante_andere_zaken"]) > 0:
            zaak_data["relaties"] = _("Yes")
        else:
            zaak_data["relaties"] = _("No")

        zaken_data.append(zaak_data)

    return zaken_data, bytes_deleted


def create_html_report_content(
    zaken_data: List[dict], bytes_deleted: int, contains_sensitive_info: bool
) -> str:

    return render(
        request=None,
        template_name="report/vernietigings_rapport.html",
        context={
            "destroyed_zaken": zaken_data,
            "contains_sensitive_info": contains_sensitive_info,
            "bytes_deleted": filesizeformat(bytes_deleted),
        },
    ).content.decode("utf8")


def create_csv_report_content(
    zaken_data: List[dict], contains_sensitive_info: bool
) -> io.StringIO:
    column_names = {
        "identificatie": _("Unique ID"),
        "omschrijving": _("Description"),
        "looptijd": _("Duration"),
        "vernietigings_categorie": _("Destruction category Selectielijst"),
        "toelichting": _("Explanation"),
        "opmerkingen": _("Remarks SAD"),
        "reactie_zorgdrager": _("Reaction caretaker"),
        "zaaktype": _("Case type"),
        "archiefactietermijn": _("Archive action period"),
        "resultaattype": _("Result type"),
        "verantwoordelijke_organisatie": _("Organisation responsible"),
        "relaties": _("Relations"),
    }

    optional_columns = ["omschrijving", "opmerkingen"]

    report_columns = [
        value
        for key, value in column_names.items()
        if not (key in optional_columns and contains_sensitive_info)
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=report_columns)

    writer.writeheader()
    for zaak in zaken_data:
        row_data = {
            value: zaak.get(key) or ""
            for key, value in column_names.items()
            if not (key in optional_columns and contains_sensitive_info)
        }

        writer.writerow(row_data)

    output.seek(0)

    return output


def create_destruction_report_subject(destruction_list: DestructionList) -> str:
    subject = _("Declaration of destruction - %(name)s (%(date)s)") % {
        "name": destruction_list.name,
        "date": datetime.strftime(destruction_list.created, "%Y-%m-%d"),
    }
    return subject


def convert_to_pdf(html_content: str) -> ByteString:
    html_object = HTML(string=html_content)
    return html_object.write_pdf()


def create_destruction_report(destruction_list: DestructionList) -> DestructionReport:
    zaken_data_for_report, bytes_deleted = get_destruction_report_data(destruction_list)

    report_content_html = create_html_report_content(
        zaken_data_for_report, bytes_deleted, destruction_list.contains_sensitive_info
    )
    audittrail_html = create_audittrail_report(destruction_list)
    report_content_csv = create_csv_report_content(
        zaken_data_for_report, destruction_list.contains_sensitive_info
    )
    report_subject = create_destruction_report_subject(destruction_list)

    process_owner_review = DestructionListReview.objects.filter(
        destruction_list=destruction_list,
        author__role__type=RoleTypeChoices.process_owner,
    ).last()

    report_filename = (
        f"verklaring-van-vernietiging_{destruction_list.name.replace(' ', '-')}"
    )

    destruction_report = DestructionReport.objects.create(
        title=report_subject,
        process_owner=process_owner_review.author if process_owner_review else None,
        content_pdf=ContentFile(
            content=convert_to_pdf(report_content_html + audittrail_html),
            name=f"{report_filename}.pdf",
        ),
        content_csv=ContentFile(
            content=report_content_csv.read(), name=f"{report_filename}.csv"
        ),
        destruction_list=destruction_list,
    )

    return destruction_report


def get_absolute_url(path: str, request: Optional[HttpRequest] = None) -> str:
    if request is not None:
        return request.build_absolute_uri(path)

    site = Site.objects.get_current()
    protocol = "https" if settings.IS_HTTPS else "http"
    return f"{protocol}://{site.domain}{path}"


def create_audittrail_report(destruction_list: DestructionList):
    list_logs = destruction_list.logs.all()
    reviews_logs = [review.logs.all() for review in destruction_list.reviews.all()]
    all_logs = sorted(
        chain(*reviews_logs, list_logs), key=lambda instance: instance.timestamp
    )

    return render(
        request=None,
        template_name="report/audittrail/audittrail.html",
        context={"logs": all_logs},
    ).content.decode("utf8")
