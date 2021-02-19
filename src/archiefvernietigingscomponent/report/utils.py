import uuid
from datetime import date, datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
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


def get_vernietigings_categorie_selectielijst(zaaktype: str) -> str:
    try:
        zaaktype = fetch_zaaktype(zaaktype)
    except ClientError as exc:
        # If the zaaktype couldn't be retrieved, return an empty value
        return ""

    if not zaaktype.get("selectielijstProcestype"):
        return ""

    try:
        process_type = fetch_process_type(zaaktype["selectielijstProcestype"])
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
        zaak_data["looptijd"] = _("%(looptijd)s days") % {
            "looptijd": get_looptijd(zaak_data)
        }
        zaak_data[
            "vernietigings_categorie"
        ] = get_vernietigings_categorie_selectielijst(zaak_data["zaaktype"])
        zaak_data["toelichting"] = _("Part of destructionlist: %(name)s") % {
            "name": destruction_list.name
        }
        zaak_data["opmerkingen"] = get_destruction_list_archivaris_comments(
            destruction_list
        )
        zaak_data["reactie_zorgdrager"] = get_process_owner_comments(destruction_list)
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

    destruction_report = DestructionReport.objects.create(
        title=report_subject,
        process_owner=process_owner_review.author if process_owner_review else None,
        content=ContentFile(content=report_content, name=f"{uuid.uuid4()}.html"),
    )

    return destruction_report


def get_absolute_url(path: str) -> str:
    site = Site.objects.get_current()
    protocol = "https" if settings.IS_HTTPS else "http"
    return f"{protocol}://{site.domain}{path}"
