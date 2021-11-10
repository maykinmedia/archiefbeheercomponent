import logging
import re
from typing import Optional

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from zds_client import ClientError

from archiefvernietigingscomponent.report.utils import get_looptijd

from .constants import ListItemStatus
from .models import (
    BRONORGANISATIE_TEMPLATE_ELEMENT,
    IDENTIFICATIE_TEMPLATE_ELEMENT,
    UUID_TEMPLATE_ELEMENT,
    ZAC_TEMPLATE_ELEMENTS,
    DestructionListItem,
)
from .service import fetch_process_type, fetch_resultaat

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


class ServiceNotConfiguredError(Exception):
    pass
