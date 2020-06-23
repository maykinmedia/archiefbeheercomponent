from zds_client.client import ClientError
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service
from zgw_consumers.service import get_paginated_results


def _client_from_url(url: str):
    service = Service.get_service(url)
    if not service:
        raise ClientError("There is no Service configured for %r" % url)
    return service.build_client()


# ZTC
def get_zaaktypen() -> list:
    zaaktypen = []

    for ztc in Service.objects.filter(api_type=APITypes.ztc):
        client = ztc.build_client()
        zaaktypen += get_paginated_results(client, "zaaktype")

    return zaaktypen


# ZRC
def get_zaken(query_params=None) -> list:
    query_params = query_params or {}

    zaken = []
    for zrc in Service.objects.filter(api_type=APITypes.zrc):
        client = zrc.build_client()
        zaken += get_paginated_results(
            client, "zaak", minimum=25, query_params=query_params
        )

    "resolve zaaktype url"
    fetched_zaaktypen = {zaaktype["url"]: zaaktype for zaaktype in get_zaaktypen()}
    for zaak in zaken:
        zaak["zaaktype"] = fetched_zaaktypen[zaak["zaaktype"]]

    zaken = sorted(
        zaken,
        key=lambda zaak: (
            zaak["registratiedatum"],
            zaak["startdatum"],
            zaak["identificatie"],
        ),
        reverse=True,
    )
    return zaken


def fetch_zaak(url) -> dict:
    client = _client_from_url(url)
    response = client.retrieve("zaak", url=url)
    return response


def remove_zaak(url: str) -> None:
    """
    Destroy the Zaak and related objects identified by the zaak URL.
    """
    zrc_client = _client_from_url(url)

    # find and destroy related besluiten
    zaak_uuid = url.rstrip("/").split("/")[-1]
    zaakbesluiten = zrc_client.list("zaakbesluit", zaak_uuid=zaak_uuid)

    for zaakbesluit in zaakbesluiten:
        besluit_url = zaakbesluit["besluit"]
        brc_client = _client_from_url(besluit_url)
        brc_client.delete("besluit", url=besluit_url)

    # destroy zaak
    zios = zrc_client.list("zaakinformatieobject", query_params={"zaak": url})
    zrc_client.delete("zaak", url=url)

    # find and destroy related documenten
    for zio in zios:
        io_url = zio["informatieobject"]

        drc_client = _client_from_url(io_url)
        # check if documents have pending relations
        oios = drc_client.list(
            "objectinformatieobject", query_params={"informatieobject": io_url}
        )
        if not oios:
            drc_client.delete("enkelvoudiginformatieobject", url=io_url)
