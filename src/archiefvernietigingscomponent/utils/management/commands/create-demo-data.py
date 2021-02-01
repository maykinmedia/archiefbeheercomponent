from base64 import b64encode

from django.core.management.base import BaseCommand

from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

CATALOGUS = {
    "domein": "CATAL",
    "rsin": "104567387",
    "contactpersoonBeheerNaam": "Jane Doe",
}


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

        # Create a catalogus
        catalogus = ztc_client.create(resource="catalogus", data=CATALOGUS)

        # Create zaaktypes and informatie objecttypes
        zaaktype_1 = ztc_client.create(
            resource="zaaktype",
            data={
                "omschrijving": "Zaaktype 1",
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
            },
        )
        zaaktype_2 = ztc_client.create(
            resource="zaaktype",
            data={
                "omschrijving": "Zaaktype 2",
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
            },
        )

        informatieobjecttype_1 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": "IOT type 1",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
            },
        )
        informatieobjecttype_2 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": "IOT type 2",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
            },
        )
        informatieobjecttype_3 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": "IOT type 3",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
            },
        )
        informatieobjecttype_4 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": "IOT type 4",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
            },
        )

        # Create 2 zaken for the first zaaktype
        zaak_1 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "517439943",
                "omschrijving": "Test zaak 1",
                "zaaktype": zaaktype_1["url"],
                "vertrouwelijkheidaanduiding": "openbaar",
                "startdatum": "2021-05-01",
                "verantwoordelijkeOrganisatie": "104567387",
            },
        )
        zaak_2 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "517439943",
                "omschrijving": "Test zaak 2",
                "zaaktype": zaaktype_1["url"],
                "vertrouwelijkheidaanduiding": "geheim",
                "startdatum": "2021-07-01",
                "verantwoordelijkeOrganisatie": "104567387",
            },
        )

        # Create a document for each zaak of the first zaaktype
        document_1 = drc_client.create(
            resource="enkelvoudiginformatieobject",
            data={
                "bronorganisatie": "517439943",
                "creatiedatum": "2021-01-01",
                "titel": "Test document 1",
                "Auteur": "John Doe",
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
                "titel": "Test document 2",
                "Auteur": "John Doe",
                "taal": "nld",
                "formaat": "txt",
                "inhoud": b64encode(b"Test text file").decode("utf-8"),
                "informatieobjecttype": informatieobjecttype_2["url"],
            },
        )

        # Relate the documents to the zaken
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

        zrc_client.create(
            resource="zaakinformatieobject",
            data={"zaak": zaak_1["url"], "informatieobject": document_1["url"],},
        )
        zrc_client.create(
            resource="zaakinformatieobject",
            data={"zaak": zaak_2["url"], "informatieobject": document_2["url"],},
        )

        # Create 2 zaken for the second zaaktype
        zaak_3 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "517439943",
                "omschrijving": "Test zaak 3",
                "zaaktype": zaaktype_2["url"],
                "vertrouwelijkheidaanduiding": "openbaar",
                "startdatum": "2021-05-01",
                "verantwoordelijkeOrganisatie": "104567387",
            },
        )
        zaak_4 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "517439943",
                "omschrijving": "Test zaak 4",
                "zaaktype": zaaktype_2["url"],
                "vertrouwelijkheidaanduiding": "geheim",
                "startdatum": "2021-07-01",
                "verantwoordelijkeOrganisatie": "104567387",
            },
        )

        # Create a document for each zaak of the second zaaktype
        document_3 = drc_client.create(
            resource="enkelvoudiginformatieobject",
            data={
                "bronorganisatie": "517439943",
                "creatiedatum": "2021-01-01",
                "titel": "Test document 3",
                "Auteur": "John Doe",
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
                "titel": "Test document 4",
                "Auteur": "John Doe",
                "taal": "nld",
                "formaat": "txt",
                "inhoud": b64encode(b"Test text file").decode("utf-8"),
                "informatieobjecttype": informatieobjecttype_4["url"],
            },
        )

        # Relate the documents to the zaken
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

        zrc_client.create(
            resource="zaakinformatieobject",
            data={"zaak": zaak_3["url"], "informatieobject": document_3["url"],},
        )
        zrc_client.create(
            resource="zaakinformatieobject",
            data={"zaak": zaak_4["url"], "informatieobject": document_4["url"],},
        )

        self.stdout.write(self.style.SUCCESS("Successfully created demo data."))
