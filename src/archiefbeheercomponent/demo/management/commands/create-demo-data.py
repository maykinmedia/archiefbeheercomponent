from base64 import b64encode

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string as _get_random_string

from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from ..constants import DEFAULT_CATALOGUS
from ..utils import get_or_create_catalogus, uuid_from_url


def get_random_string(number: int = 6) -> str:
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return _get_random_string(length=number, allowed_chars=allowed_chars)


class Command(BaseCommand):
    help = "Create demo data in Open-Zaak"

    def handle(self, *args, **options):
        # Get the Clients for the Catalogi, Zaken and Documenten APIs.
        ztc_service = Service.objects.filter(api_type=APITypes.ztc).first()
        assert ztc_service, "No service defined for the Catalogi API"
        ztc_client = ztc_service.build_client()
        zrc_service = Service.objects.filter(api_type=APITypes.zrc).first()
        assert zrc_service, "No service defined for the Zaken API"
        zrc_client = zrc_service.build_client()

        drc_service = Service.objects.filter(api_type=APITypes.drc).first()
        assert drc_service, "No service defined for the Documenten API"
        drc_client = drc_service.build_client()

        catalogus = get_or_create_catalogus(DEFAULT_CATALOGUS, ztc_client)

        procestype_1 = "https://selectielijst.openzaak.nl/api/v1/procestypen/e1b73b12-b2f6-4c4e-8929-94f84dd2a57d"

        # Create zaaktypes and informatie objecttypes
        zaaktype_1 = ztc_client.create(
            resource="zaaktype",
            data={
                "omschrijving": f"Zaaktype {get_random_string()}",
                "vertrouwelijkheidaanduiding": "openbaar",
                "doel": "Zaaktype doel 1",
                "aanleiding": "aanleiding 1",
                "indicatieInternOfExtern": "intern",
                "handelingInitiator": "aangeven",
                "onderwerp": "onderwerp 1",
                "handelingBehandelaar": "behandelen",
                "doorlooptijd": "P30D",
                "opschortingEnAanhoudingMogelijk": False,
                "verlengingMogelijk": False,
                "publicatieIndicatie": True,
                "productenOfDiensten": [],
                "catalogus": catalogus["url"],
                "besluittypen": [],
                "gerelateerdeZaaktypen": [],
                "beginGeldigheid": "2021-01-01",
                "versiedatum": "2021-01-01",
                "referentieproces": {"naam": "Proces naam 1", "link": ""},
                "verantwoordelijke": "Chef Kok",
                "selectielijstProcestype": procestype_1,
            },
        )
        zaaktype_2 = ztc_client.create(
            resource="zaaktype",
            data={
                "omschrijving": f"Zaaktype {get_random_string()}",
                "vertrouwelijkheidaanduiding": "openbaar",
                "doel": "Zaaktype doel 2",
                "aanleiding": "aanleiding 2",
                "indicatieInternOfExtern": "intern",
                "handelingInitiator": "aangeven",
                "onderwerp": "onderwerp 2",
                "handelingBehandelaar": "behandelen",
                "doorlooptijd": "P30D",
                "opschortingEnAanhoudingMogelijk": False,
                "verlengingMogelijk": False,
                "publicatieIndicatie": True,
                "productenOfDiensten": [],
                "catalogus": catalogus["url"],
                "besluittypen": [],
                "gerelateerdeZaaktypen": [],
                "beginGeldigheid": "2021-01-01",
                "versiedatum": "2021-01-01",
                "referentieproces": {"naam": "Proces naam 1", "link": ""},
                "verantwoordelijke": "Chef Kok",
                "selectielijstProcestype": procestype_1,
            },
        )

        informatieobjecttype_1 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": f"IOT {get_random_string()}",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
                "informatieobjectcategorie": "Voorbeeld",
            },
        )
        informatieobjecttype_2 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": f"IOT {get_random_string()}",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
                "informatieobjectcategorie": "Voorbeeld",
            },
        )
        informatieobjecttype_3 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": f"IOT {get_random_string()}",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
                "informatieobjectcategorie": "Voorbeeld",
            },
        )
        informatieobjecttype_4 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": f"IOT {get_random_string()}",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
                "informatieobjectcategorie": "Voorbeeld",
            },
        )

        # Add relations between zaaktypen and informatieobjecttypen
        ztc_client.create(
            resource="zaakinformatieobjecttype",
            data={
                "zaaktype": zaaktype_1["url"],
                "informatieobjecttype": informatieobjecttype_1["url"],
                "volgnummer": 1,
                "richting": "inkomend",
            },
        )
        ztc_client.create(
            resource="zaakinformatieobjecttype",
            data={
                "zaaktype": zaaktype_1["url"],
                "informatieobjecttype": informatieobjecttype_2["url"],
                "volgnummer": 2,
                "richting": "inkomend",
            },
        )
        ztc_client.create(
            resource="zaakinformatieobjecttype",
            data={
                "zaaktype": zaaktype_2["url"],
                "informatieobjecttype": informatieobjecttype_3["url"],
                "volgnummer": 1,
                "richting": "inkomend",
            },
        )
        ztc_client.create(
            resource="zaakinformatieobjecttype",
            data={
                "zaaktype": zaaktype_2["url"],
                "informatieobjecttype": informatieobjecttype_4["url"],
                "volgnummer": 2,
                "richting": "inkomend",
            },
        )

        ztc_client.create(
            resource="roltype",
            data={
                "zaaktype": zaaktype_1["url"],
                "omschrijving": f"Roltype: {get_random_string()}",
                "omschrijvingGeneriek": "behandelaar",
            },
        )

        ztc_client.create(
            resource="roltype",
            data={
                "zaaktype": zaaktype_2["url"],
                "omschrijving": f"Roltype: {get_random_string()}",
                "omschrijvingGeneriek": "behandelaar",
            },
        )

        resultaattypeomschrijving_1 = "https://selectielijst.openzaak.nl/api/v1/resultaattypeomschrijvingen/ce8cf476-0b59-496f-8eee-957a7c6e2506"  # noqa: E501
        selectielijstklasse_1 = "https://selectielijst.openzaak.nl/api/v1/resultaten/cc5ae4e3-a9e6-4386-bcee-46be4986a829"  # noqa: E501

        ztc_client.create(
            resource="resultaattype",
            data={
                "zaaktype": zaaktype_1["url"],
                "omschrijving": f"Resultaattype: {get_random_string()}",
                "resultaattypeomschrijving": resultaattypeomschrijving_1,
                "selectielijstklasse": selectielijstklasse_1,
                "brondatumArchiefprocedure": {
                    "afleidingswijze": "afgehandeld",
                    "datumkenmerk": "",
                    "einddatumBekend": False,
                    "objecttype": "",
                    "registratie": "",
                    "procestermijn": None,
                },
            },
        )

        ztc_client.create(
            resource="resultaattype",
            data={
                "zaaktype": zaaktype_2["url"],
                "omschrijving": f"Resultaattype: {get_random_string()}",
                "resultaattypeomschrijving": resultaattypeomschrijving_1,
                "selectielijstklasse": selectielijstklasse_1,
                "brondatumArchiefprocedure": {
                    "afleidingswijze": "afgehandeld",
                    "datumkenmerk": "",
                    "einddatumBekend": False,
                    "objecttype": "",
                    "registratie": "",
                    "procestermijn": None,
                },
            },
        )

        ztc_client.create(
            resource="statustype",
            data={
                "omschrijving": f"Statustype: {get_random_string()}",
                "zaaktype": zaaktype_1["url"],
                "volgnummer": 1,
            },
        )

        ztc_client.create(
            resource="statustype",
            data={
                "omschrijving": f"Statustype: {get_random_string()}",
                "zaaktype": zaaktype_1["url"],
                "volgnummer": 2,
            },
        )

        ztc_client.create(
            resource="statustype",
            data={
                "omschrijving": f"Statustype: {get_random_string()}",
                "zaaktype": zaaktype_2["url"],
                "volgnummer": 1,
            },
        )

        ztc_client.create(
            resource="statustype",
            data={
                "omschrijving": f"Statustype: {get_random_string()}",
                "zaaktype": zaaktype_2["url"],
                "volgnummer": 2,
            },
        )

        # Publish zaaktypen/informatieobjecttypen
        informatieobjecttypes = [
            informatieobjecttype_1,
            informatieobjecttype_2,
            informatieobjecttype_3,
            informatieobjecttype_4,
        ]
        for iot in informatieobjecttypes:
            ztc_client.operation(
                operation_id="informatieobjecttype_publish",
                data={},
                uuid=uuid_from_url(iot["url"]),
            )

        ztc_client.operation(
            operation_id="zaaktype_publish",
            data={},
            uuid=uuid_from_url(zaaktype_1["url"]),
        )
        ztc_client.operation(
            operation_id="zaaktype_publish",
            data={},
            uuid=uuid_from_url(zaaktype_2["url"]),
        )

        # Create 2 zaken for the first zaaktype
        zaak_1 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "095847261",
                "omschrijving": f"Test zaak {get_random_string()}",
                "zaaktype": zaaktype_1["url"],
                "vertrouwelijkheidaanduiding": "openbaar",
                "startdatum": "2021-05-01",
                "verantwoordelijkeOrganisatie": "104567387",
                "archiefnominatie": "vernietigen",
                "archiefstatus": "nog_te_archiveren",
                "archiefactiedatum": "2021-02-01",
            },
            request_kwargs={"headers": {"Accept-Crs": "EPSG:4326"}},
        )
        zaak_2 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "517439943",
                "omschrijving": f"Test zaak {get_random_string()}",
                "zaaktype": zaaktype_1["url"],
                "vertrouwelijkheidaanduiding": "geheim",
                "startdatum": "2021-02-01",
                "verantwoordelijkeOrganisatie": "104567387",
                "archiefnominatie": "vernietigen",
                "archiefstatus": "nog_te_archiveren",
                "archiefactiedatum": "2021-01-01",
            },
            request_kwargs={"headers": {"Accept-Crs": "EPSG:4326"}},
        )

        # Create a document for each zaak of the first zaaktype
        document_1 = drc_client.create(
            resource="enkelvoudiginformatieobject",
            data={
                "bronorganisatie": "517439943",
                "creatiedatum": "2021-01-01",
                "titel": f"Test document {get_random_string()}",
                "auteur": "John Doe",
                "taal": "nld",
                "formaat": "txt",
                "inhoud": b64encode(b"Test text file").decode("utf-8"),
                "informatieobjecttype": informatieobjecttype_1["url"],
            },
        )
        document_2 = drc_client.create(
            resource="enkelvoudiginformatieobject",
            data={
                "bronorganisatie": "517439943",
                "creatiedatum": "2021-07-01",
                "titel": f"Test document {get_random_string()}",
                "auteur": "John Doe",
                "taal": "nld",
                "formaat": "txt",
                "inhoud": b64encode(b"Test text file").decode("utf-8"),
                "informatieobjecttype": informatieobjecttype_2["url"],
            },
        )

        # Relate the documents to the zaken
        zrc_client.create(
            resource="zaakinformatieobject",
            data={
                "zaak": zaak_1["url"],
                "informatieobject": document_1["url"],
            },
        )
        zrc_client.create(
            resource="zaakinformatieobject",
            data={
                "zaak": zaak_2["url"],
                "informatieobject": document_2["url"],
            },
        )

        # Create 2 zaken for the second zaaktype
        zaak_3 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "517439943",
                "omschrijving": f"Test zaak {get_random_string()}",
                "zaaktype": zaaktype_2["url"],
                "vertrouwelijkheidaanduiding": "openbaar",
                "startdatum": "2019-01-01",
                "verantwoordelijkeOrganisatie": "104567387",
                "archiefnominatie": "vernietigen",
                "archiefstatus": "nog_te_archiveren",
                "archiefactiedatum": "2021-01-01",
            },
            request_kwargs={"headers": {"Accept-Crs": "EPSG:4326"}},
        )
        zaak_4 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "376924512",
                "omschrijving": f"Test zaak {get_random_string()}",
                "zaaktype": zaaktype_2["url"],
                "vertrouwelijkheidaanduiding": "geheim",
                "startdatum": "2021-01-01",
                "verantwoordelijkeOrganisatie": "104567387",
                "archiefnominatie": "vernietigen",
                "archiefstatus": "nog_te_archiveren",
                "archiefactiedatum": "2021-01-01",
            },
            request_kwargs={"headers": {"Accept-Crs": "EPSG:4326"}},
        )

        # Create a document for each zaak of the second zaaktype
        document_3 = drc_client.create(
            resource="enkelvoudiginformatieobject",
            data={
                "bronorganisatie": "517439943",
                "creatiedatum": "2021-01-01",
                "titel": f"Test document {get_random_string()}",
                "auteur": "John Doe",
                "taal": "nld",
                "formaat": "txt",
                "inhoud": b64encode(b"Test text file").decode("utf-8"),
                "informatieobjecttype": informatieobjecttype_3["url"],
            },
        )
        document_4 = drc_client.create(
            resource="enkelvoudiginformatieobject",
            data={
                "bronorganisatie": "517439943",
                "creatiedatum": "2021-07-01",
                "titel": f"Test document {get_random_string()}",
                "auteur": "John Doe",
                "taal": "nld",
                "formaat": "txt",
                "inhoud": b64encode(b"Test text file").decode("utf-8"),
                "informatieobjecttype": informatieobjecttype_4["url"],
            },
        )

        # Relate the documents to the zaken
        zrc_client.create(
            resource="zaakinformatieobject",
            data={
                "zaak": zaak_3["url"],
                "informatieobject": document_3["url"],
            },
        )
        zrc_client.create(
            resource="zaakinformatieobject",
            data={
                "zaak": zaak_4["url"],
                "informatieobject": document_4["url"],
            },
        )

        self.stdout.write(self.style.SUCCESS("Successfully created demo data."))
