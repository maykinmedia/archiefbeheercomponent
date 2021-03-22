import logging

from django.utils.translation import ugettext_lazy as _

from zds_client import ClientError

from archiefvernietigingscomponent.destruction.service import (
    fetch_process_type,
    fetch_resultaat,
)
from archiefvernietigingscomponent.report.utils import get_looptijd

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
