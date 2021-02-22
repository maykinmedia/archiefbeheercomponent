import uuid
from datetime import date, datetime
from typing import Optional

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.translation import gettext as _

from zds_client import ClientError

from archiefvernietigingscomponent.constants import RoleTypeChoices
from archiefvernietigingscomponent.destruction.constants import (
    ListItemStatus,
    ReviewStatus,
)
from archiefvernietigingscomponent.destruction.models import (
    DestructionList,
    DestructionListReview,
)
from archiefvernietigingscomponent.destruction.service import (
    fetch_process_type,
    fetch_zaaktype,
)
from archiefvernietigingscomponent.report.models import DestructionReport


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
    except ClientError as exc:
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
    except ClientError as exc:
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


def create_destruction_report_content(destruction_list: DestructionList) -> str:
    destroyed_items = destruction_list.items.filter(
        status=ListItemStatus.destroyed
    ).order_by("id")

    zaken_data = []
    for destroyed_item in destroyed_items:
        zaak_data = destroyed_item.extra_zaak_data

        zaaktype = get_zaaktype(zaak_data["zaaktype"])

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
        zaak_data["opmerkingen"] = get_destruction_list_archivaris_comments(
            destruction_list
        )
        zaak_data["reactie_zorgdrager"] = get_process_owner_comments(destruction_list)
        zaak_data["zaaktype"] = (
            zaaktype["omschrijving"] if zaaktype.get("omschrijving") else ""
        )

        if zaak_data.get("resultaat"):
            resultaattype = zaak_data["resultaat"]["resultaattype"]
            zaak_data["resultaattype"] = resultaattype["omschrijving"]
            zaak_data["archiefactietermijn"] = (
                resultaattype["archiefactietermijn"]
                if resultaattype.get("archiefactietermijn")
                else ""
            )

        if len(zaak_data["relevante_andere_zaken"]) > 0:
            zaak_data["relaties"] = _("Ja")
        else:
            zaak_data["relaties"] = _("Nee")

        zaken_data.append(zaak_data)

    return render(
        request=None,
        template_name="report/vernietigings_rapport.html",
        context={"destroyed_zaken": zaken_data},
    ).content.decode("utf8")


def create_destruction_report_subject(destruction_list: DestructionList) -> str:
    subject = _("Declaration of destruction - %(name)s (%(date)s)") % {
        "name": destruction_list.name,
        "date": datetime.strftime(destruction_list.created, "%Y-%m-%d"),
    }
    return subject


def create_destruction_report(destruction_list: DestructionList) -> DestructionReport:
    report_content = create_destruction_report_content(destruction_list)
    report_subject = create_destruction_report_subject(destruction_list)

    process_owner_review = DestructionListReview.objects.filter(
        destruction_list=destruction_list,
        author__role__type=RoleTypeChoices.process_owner,
    ).last()

    report_filename = (
        f"verklaring-van-vernietiging_{destruction_list.name.replace(' ', '-')}.pdf"
    )

    destruction_report = DestructionReport.objects.create(
        title=report_subject,
        process_owner=process_owner_review.author if process_owner_review else None,
        content=ContentFile(content=report_content, name=report_filename),
    )

    return destruction_report


def get_absolute_url(path: str, request: Optional[HttpRequest] = None) -> str:
    if request is not None:
        return request.build_absolute_uri(path)

    site = Site.objects.get_current()
    protocol = "https" if settings.IS_HTTPS else "http"
    return f"{protocol}://{site.domain}{path}"
