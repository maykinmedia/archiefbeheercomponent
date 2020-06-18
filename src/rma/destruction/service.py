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


def remove_zaak(url) -> None:
    client = _client_from_url(url)
    client.delete("zaak", url=url)
