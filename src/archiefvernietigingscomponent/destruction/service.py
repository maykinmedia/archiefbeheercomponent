from typing import Optional, Union

from zds_client.client import ClientError
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service
from zgw_consumers.service import get_paginated_results


def _client_from_url(url: str):
    service = Service.get_service(url)
    if not service:
        raise ClientError("There is no Service configured for %r" % url)
    return service.build_client()


def _uuid_from_url(url: str):
    return url.rstrip("/").split("/")[-1]


# ZTC
def get_types_generic(type_name, dict_response=False) -> Union[list, dict]:
    typen = []

    for ztc in Service.objects.filter(api_type=APITypes.ztc):
        client = ztc.build_client()
        typen += get_paginated_results(client, type_name)

    if not dict_response:
        return typen

    return {t["url"]: t for t in typen}


def get_zaaktypen(dict_response=False) -> list:
    return get_types_generic("zaaktype", dict_response)


def get_informatieobjecttypen(dict_response=False) -> list:
    return get_types_generic("informatieobjecttype", dict_response)


def get_besluittypen(dict_response=False) -> list:
    return get_types_generic("besluittype", dict_response)


def fetch_zaaktype(url: str) -> dict:
    client = _client_from_url(url)
    response = client.retrieve("zaaktype", url=url)
    return response


# ZRC
def get_zaken(query_params=None) -> list:
    query_params = query_params or {}
    if sort_by_zaaktype := query_params.get("sort_by_zaaktype"):
        query_params = query_params.copy()
        del query_params["sort_by_zaaktype"]

    zaken = []
    for zrc in Service.objects.filter(api_type=APITypes.zrc):
        client = zrc.build_client()
        zaken += get_paginated_results(
            client, "zaak", minimum=25, query_params=query_params
        )

    # Resolve zaaktype url
    fetched_zaaktypen = get_zaaktypen(dict_response=True)
    for zaak in zaken:
        zaak["zaaktype"] = fetched_zaaktypen[zaak["zaaktype"]]

    if sort_by_zaaktype:
        zaken = sorted(zaken, key=lambda zaak: (zaak["zaaktype"]["omschrijving"]))

    return zaken


def fetch_zaak(url: str) -> dict:
    client = _client_from_url(url)
    response = client.retrieve("zaak", url=url)
    return response


def update_zaak(url: str, data: dict, audit_comment: Optional[str]) -> dict:
    client = _client_from_url(url)
    headers = {
        "X-Audit-Toelichting": f"[Archiefvernietigingscomponent] {audit_comment}"
    }
    response = client.partial_update(
        "zaak", url=url, data=data, request_kwargs={"headers": headers}
    )
    return response


def remove_zaak(url: str) -> None:
    """
    Destroy the Zaak and related objects identified by the zaak URL.
    """
    zrc_client = _client_from_url(url)

    # find and destroy related besluiten
    zaak_uuid = _uuid_from_url(url)
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


def get_resultaat(zaak_url: str) -> Optional[dict]:
    zaak = fetch_zaak(zaak_url)
    resultaat_url = zaak["resultaat"]

    if not resultaat_url:
        return None

    resultaat = fetch_resultaat(resultaat_url)
    resultaat["zaak"] = zaak

    return resultaat


def fetch_resultaat(resultaat_url: str) -> dict:
    zrc_client = _client_from_url(resultaat_url)
    resultaat = zrc_client.retrieve("resultaat", url=resultaat_url)

    resultaattype_url = resultaat["resultaattype"]
    ztc_client = _client_from_url(resultaattype_url)
    resultaattype = ztc_client.retrieve("resultaattype", url=resultaattype_url)

    resultaat["resultaattype"] = resultaattype

    return resultaat


# DRC
def get_documenten(zaak_url: str) -> list:
    zrc_client = _client_from_url(zaak_url)
    zios = zrc_client.list("zaakinformatieobject", query_params={"zaak": zaak_url})

    documenten = []
    #  TODO async
    for zio in zios:
        io_url = zio["informatieobject"]
        drc_client = _client_from_url(io_url)
        document = drc_client.retrieve("enkelvoudiginformatieobject", url=io_url)
        documenten.append(document)

    fetched_iotypen = get_informatieobjecttypen(dict_response=True)

    for document in documenten:
        document["informatieobjecttype"] = fetched_iotypen[
            document["informatieobjecttype"]
        ]

    return documenten


# BRC
def get_besluiten(zaak_url: str) -> list:
    zrc_client = _client_from_url(zaak_url)
    zaak_uuid = _uuid_from_url(zaak_url)
    zaakbesluiten = zrc_client.list("zaakbesluit", zaak_uuid=zaak_uuid)

    # TODO async
    besluiten = []
    for zaakbesluit in zaakbesluiten:
        besluit_url = zaakbesluit["besluit"]
        brc_client = _client_from_url(besluit_url)
        besluit = brc_client.retrieve("besluit", url=besluit_url)
        besluiten.append(besluit)

    fetched_besluittypen = get_besluittypen(dict_response=True)

    for besluit in besluiten:
        besluit["besluittype"] = fetched_besluittypen[besluit["besluittype"]]

    return besluiten


# SELECTIELIJST
def fetch_process_type(url: str) -> dict:
    client = _client_from_url(url)
    response = client.retrieve("procestype", url=url)
    return response
