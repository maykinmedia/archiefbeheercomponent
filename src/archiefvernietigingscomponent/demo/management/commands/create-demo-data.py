from base64 import b64encode
from datetime import datetime

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
        date = datetime.now()
        ztc_service = Service.objects.filter(api_type=APITypes.ztc).first()
        assert ztc_service, "No service defined for the Catalogi API"
        ztc_client = ztc_service.build_client()
        zrc_service = Service.objects.filter(api_type=APITypes.zrc).first()
        assert zrc_service, "No service defined for the Zaken API"
        zrc_client = zrc_service.build_client()

        drc_service = Service.objects.filter(api_type=APITypes.drc).first()
        assert drc_service, "No service defined for the Documenten API"
        drc_client = drc_service.build_client()

        # Create a catalogus if one doesn't exist already
        catalogus_list = ztc_client.list(
            resource="catalogus", query_params={"domein": CATALOGUS['domein'], "rsin": CATALOGUS['rsin'],}
        )

        if len(catalogus_list["results"]) == 0:
            catalogus = ztc_client.create(resource="catalogus", data=CATALOGUS)
        else:
            catalogus = catalogus_list["results"][0]
        # Create zaaktypes and informatie objecttypes
        zaaktype_1 = ztc_client.create(
            resource="zaaktype",
            data={
                "omschrijving": f"Zaaktype 1 {date}",
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
                "omschrijving": f"Zaaktype 2 {date}",
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
                "omschrijving": f"IOT type 1 {date}",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
            },
        )
        # pdb.set_trace()
        informatieobjecttype_2 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": f"IOT type 2 {date}",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
            },
        )
        informatieobjecttype_3 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": f"IOT type 3 {date}",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
            },
        )
        informatieobjecttype_4 = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": f"IOT type 4 {date}",
                "vertrouwelijkheidaanduiding": "openbaar",
                "beginGeldigheid": "2021-01-01",
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
                uuid=iot["url"].split("/")[-1],
            )

        ztc_client.operation(
            operation_id="zaaktype_publish",
            data={},
            uuid=zaaktype_1["url"].split("/")[-1],
        )
        ztc_client.operation(
            operation_id="zaaktype_publish",
            data={},
            uuid=zaaktype_2["url"].split("/")[-1],
        )

        # Create 2 zaken for the first zaaktype
        zaak_1 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "095847261",
                "omschrijving": f"Test zaak 1 {date}",
                "zaaktype": zaaktype_1["url"],
                "vertrouwelijkheidaanduiding": "openbaar",
                "startdatum": "2021-05-01",
                "verantwoordelijkeOrganisatie": "104567387",
                "archiefnominatie": "vernietigen",
                "archiefstatus": "nog_te_archiveren",
                "archiefactiedatum": "2021-02-01",
            },
        )
        zaak_2 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "517439943",
                "omschrijving": f"Test zaak 2 {date}",
                "zaaktype": zaaktype_1["url"],
                "vertrouwelijkheidaanduiding": "geheim",
                "startdatum": "2021-02-01",
                "verantwoordelijkeOrganisatie": "104567387",
                "archiefnominatie": "vernietigen",
                "archiefstatus": "nog_te_archiveren",
                "archiefactiedatum": "2021-01-01",
            },
        )

        # Create a document for each zaak of the first zaaktype
        document_1 = drc_client.create(
            resource="enkelvoudiginformatieobject",
            data={
                "bronorganisatie": "517439943",
                "creatiedatum": "2021-01-01",
                "titel": "Test document 1",
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
                "titel": "Test document 2",
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
                "omschrijving": f"Test zaak 3 {date}",
                "zaaktype": zaaktype_2["url"],
                "vertrouwelijkheidaanduiding": "openbaar",
                "startdatum": "2019-01-01",
                "verantwoordelijkeOrganisatie": "104567387",
                "archiefnominatie": "vernietigen",
                "archiefstatus": "nog_te_archiveren",
                "archiefactiedatum": "2021-01-01",
            },
        )
        zaak_4 = zrc_client.create(
            resource="zaak",
            data={
                "bronorganisatie": "376924512",
                "omschrijving": f"Test zaak 4 {date}",
                "zaaktype": zaaktype_2["url"],
                "vertrouwelijkheidaanduiding": "geheim",
                "startdatum": "2021-01-01",
                "verantwoordelijkeOrganisatie": "104567387",
                "archiefnominatie": "vernietigen",
                "archiefstatus": "nog_te_archiveren",
                "archiefactiedatum": "2021-01-01",
            },
        )

        # Create a document for each zaak of the second zaaktype
        document_3 = drc_client.create(
            resource="enkelvoudiginformatieobject",
            data={
                "bronorganisatie": "517439943",
                "creatiedatum": "2021-01-01",
                "titel": "Test document 3",
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
                "titel": "Test document 4",
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
            data={"zaak": zaak_3["url"], "informatieobject": document_3["url"],},
        )
        zrc_client.create(
            resource="zaakinformatieobject",
            data={"zaak": zaak_4["url"], "informatieobject": document_4["url"],},
        )

        self.stdout.write(self.style.SUCCESS("Successfully created demo data."))
