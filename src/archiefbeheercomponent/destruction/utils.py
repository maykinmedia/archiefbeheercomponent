import logging
import os
import re
from base64 import b64encode
from typing import TYPE_CHECKING, Dict, Optional

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _

from zds_client import ClientError

from archiefbeheercomponent.report.utils import get_looptijd

from .constants import ListItemStatus
from .models import (
    BRONORGANISATIE_TEMPLATE_ELEMENT,
    IDENTIFICATIE_TEMPLATE_ELEMENT,
    UUID_TEMPLATE_ELEMENT,
    ZAC_TEMPLATE_ELEMENTS,
    DestructionListItem,
)
from .service import fetch_process_type, fetch_resultaat

if TYPE_CHECKING:
    from zgw_consumers.client import ZGWClient

    from .models import ArchiveConfig, DestructionList

logger = logging.getLogger(__name__)

NO_DETAIL_PROCESSTYPE_ATTRS = ["nummer"]


def get_additional_zaak_info(zaak: dict) -> dict:
    zaaktype = zaak["zaaktype"]

    zaak["looptijd"] = _("%(duration)s days") % {"duration": get_looptijd(zaak)}

    # Retrieve the Vernietigings-categorie selectielijst
    if zaaktype.get("selectielijstProcestype"):
        try:
            process_type = fetch_process_type(zaaktype["selectielijstProcestype"])
        except ClientError:
            logger.warning("No service configured for the selectielijst.")
        else:
            process_type_data = {
                attr: process_type[attr] for attr in NO_DETAIL_PROCESSTYPE_ATTRS
            }
            zaak["zaaktype"]["processtype"] = process_type_data

    # Retrieve resultaat
    if zaak.get("resultaat"):
        zaak["resultaat"] = fetch_resultaat(zaak["resultaat"])

    return zaak


def get_zaak_link_for_zaakafhandelcomponent(
    zaak: dict, link_template: Optional[str]
) -> Optional[str]:
    if not link_template:
        return None

    for pattern in ZAC_TEMPLATE_ELEMENTS:
        if re.search(pattern, link_template):
            re_pattern = re.compile(pattern)

            if pattern == UUID_TEMPLATE_ELEMENT:
                value = zaak["uuid"]
            elif pattern == IDENTIFICATIE_TEMPLATE_ELEMENT:
                value = zaak["identificatie"]
            elif pattern == BRONORGANISATIE_TEMPLATE_ELEMENT:
                value = zaak["bronorganisatie"]

            link_template = re.sub(re_pattern, value, link_template)

    return link_template


def get_zaken_chunks(zaken):
    return (
        zaken[pos : pos + settings.ZAKEN_PER_QUERY]
        for pos in range(0, len(zaken), settings.ZAKEN_PER_QUERY)
    )


def set_zaken_availability(zaken):
    """check if selected zaken are used in other DLs"""
    zaak_urls = [zaak["url"] for zaak in zaken]
    selected_zaken = []
    for chunk in get_zaken_chunks(zaak_urls):
        selected_zaken += list(
            DestructionListItem.objects.filter(
                status__in=[ListItemStatus.suggested, ListItemStatus.processing]
            )
            .filter(zaak__in=chunk)
            .values_list("zaak", flat=True)
        )

    for zaak in zaken:
        zaak["available"] = zaak["url"] not in selected_zaken


def format_zaak_record(zaak, user):
    relations = _("No")
    if len(zaak.get("relevanteAndereZaken", [])):
        relations = _("Yes")

    user_representation = f"{user.first_name} {user.last_name}"
    resultaattype = (
        zaak.get("resultaat", {}).get("resultaattype", {}).get("omschrijving") or ""
    )
    archiefactietermijn = (
        zaak.get("resultaat", {}).get("resultaattype", {}).get("archiefactietermijn")
        or ""
    )

    return [
        zaak.get("identificatie"),
        zaak["zaaktype"]["omschrijving"],
        zaak.get("omschrijving"),
        _("%(duration)s days") % {"duration": get_looptijd(zaak)},
        zaak["verantwoordelijkeOrganisatie"],
        resultaattype,
        archiefactietermijn,
        zaak["zaaktype"].get("processtype", {}).get("nummer") or "",
        relations,
        user_representation,
    ]


class ServiceNotConfiguredError(Exception):
    pass


def add_additional_review_documents(
    destruction_list: "DestructionList",
    zaak: Dict,
    config: "ArchiveConfig",
    drc_client: "ZGWClient",
    zrc_client: "ZGWClient",
) -> None:
    """
    Add any additional documents that were uploaded during the review process
    """
    for review in destruction_list.reviews.all():
        if not review.additional_document:
            continue

        with review.additional_document.open("rb") as f:
            additional_document = drc_client.create(
                resource="enkelvoudiginformatieobject",
                data={
                    "bronorganisatie": config.source_organisation,
                    "creatiedatum": timezone.now().date().isoformat(),
                    "titel": os.path.basename(review.additional_document.name),
                    "auteur": "Archiefbeheercomponent",
                    "taal": "nld",
                    "inhoud": b64encode(f.read()).decode("utf-8"),
                    "informatieobjecttype": config.additional_review_document_type,
                    "indicatie_gebruiksrecht": False,
                },
            )

            zrc_client.create(
                resource="zaakinformatieobject",
                data={
                    "zaak": zaak["url"],
                    "informatieobject": additional_document["url"],
                },
            )
