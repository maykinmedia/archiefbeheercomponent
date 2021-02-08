from datetime import date, datetime

from django.shortcuts import render
from django.utils.translation import gettext as _

from archiefvernietigingscomponent.destruction.constants import ListItemStatus
from archiefvernietigingscomponent.destruction.models import DestructionList


def get_looptijd(zaak: dict) -> int:

    if zaak["einddatum"] != "":
        end_date = datetime.strptime(zaak["einddatum"], "%Y-%m-%d")
    else:
        end_date = date.today()

    return (end_date - datetime.strptime(zaak["startdatum"], "%Y-%m-%d")).days


def create_destruction_report(destruction_list: DestructionList) -> str:
    destroyed_items = destruction_list.items.filter(
        status=ListItemStatus.destroyed
    ).order_by("id")

    zaken_data = []
    for destroyed_item in destroyed_items:
        zaak_data = destroyed_item.extra_zaak_data
        zaak_data["looptijd"] = _(f"{get_looptijd(zaak_data)} days")
        zaak_data["vernietigings_categorie"] = ""
        zaak_data["toelichting"] = ""
        zaak_data["opmerkingen"] = ""
        zaak_data["reactie_zorgdrager"] = ""
        zaken_data.append(zaak_data)

    return render(
        request=None,
        template_name="destruction/vernietigings_rapport.html",
        context={"destroyed_zaken": zaken_data},
    ).content.decode("utf8")
