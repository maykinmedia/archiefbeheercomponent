from django.core.management.base import BaseCommand

from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from ..constants import DEFAULT_CATALOGUS
from ..utils import get_or_create_catalogus, uuid_from_url


class Command(BaseCommand):
    help = (
        "Create zaaktype, informatieobjecttype, statustype and resultaattype in open-zaak for "
        "the zaak that will be created after the destruction of a destruction list."
    )

    def handle(self, *args, **options):
        ztc_service = Service.objects.filter(api_type=APITypes.ztc).first()
        assert ztc_service, "No service defined for the Catalogi API"
        ztc_client = ztc_service.build_client()

        catalogus = get_or_create_catalogus(DEFAULT_CATALOGUS, ztc_client)

        zaaktype = ztc_client.create(
            resource="zaaktype",
            data={
                "omschrijving": "Archiefvernietiging.uitvoeren",
                "vertrouwelijkheidaanduiding": "intern",
                "toelichting": (
                    "Dit werkproces betreft het vernietigen van archiefbescheiden. De zorgdrager dient de "
                    "archiefbescheiden die in een vastgestelde selectielijst zijn aangemerkt als "
                    "'te vernietigen' ook daadwerkelijk te vernietigen. Hij dient de vernietigingslijst "
                    "voor te leggen aan de gemeentearchivaris of de archiefinspecteur. Deze kan bepaalde "
                    "archiefbescheiden uit laten zonderen van vernietiging en geeft vervolgens een "
                    "machtiging tot vernietiging af. De zorgdrager stelt vervolgens na de daadwerkelijke "
                    "vernietiging hier een verklaring van op met een specificatie van de vernietigde "
                    "archiefbescheiden (zonder persoonsgegevens)."
                ),
                "doel": "Archiefvernietiging",
                "aanleiding": "Dit werkproces wordt intern getriggerd.",
                "indicatieInternOfExtern": "intern",
                "onderwerp": "Archiefvernietiging",
                "handelingBehandelaar": "raadplegen",
                "handelingInitiator": "registreren",
                "doorlooptijd": "P365D",
                "opschortingEnAanhoudingMogelijk": True,
                "verlengingMogelijk": False,
                "publicatieIndicatie": False,
                "productenOfDiensten": [],
                "catalogus": catalogus["url"],
                "besluittypen": [],
                "gerelateerdeZaaktypen": [],
                "beginGeldigheid": "2012-10-04",
                "versiedatum": "2012-10-04",
                "referentieproces": {"naam": "Archivering", "link": ""},
                "selectielijstProcestype": (
                    "https://selectielijst.openzaak.nl/api/v1/procestypen/66b82ebc-25c0-4a15-9323-11def942a374"
                ),
            },
        )
        self.stdout.write(self.style.SUCCESS("Created zaaktype %s." % zaaktype["url"]))

        informatieobjecttype = ztc_client.create(
            resource="informatieobjecttype",
            data={
                "catalogus": catalogus["url"],
                "omschrijving": "Verklaring van vernietiging",
                "vertrouwelijkheidaanduiding": "intern",
                "beginGeldigheid": "2012-10-04",
            },
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Created informatieobjecttype %s." % informatieobjecttype["url"]
            )
        )

        ztc_client.create(
            resource="zaakinformatieobjecttype",
            data={
                "zaaktype": zaaktype["url"],
                "informatieobjecttype": informatieobjecttype["url"],
                "volgnummer": 1,
                "richting": "intern",
            },
        )
        statustype = ztc_client.create(
            resource="statustype",
            data={
                "zaaktype": zaaktype["url"],
                "volgnummer": 9,
                "omschrijving": "Afgehandeld",
                "statustekst": "Deze status markeert dat de zaak is afgesloten.",
            },
        )
        self.stdout.write(
            self.style.SUCCESS("Created statustype %s." % statustype["url"])
        )
        resultaattype = ztc_client.create(
            resource="resultaattype",
            data={
                "zaaktype": zaaktype["url"],
                "omschrijving": "Afgehandeld",
                "resultaattypeomschrijving": (
                    "https://selectielijst.openzaak.nl"
                    "/api/v1/resultaattypeomschrijvingen/7cb315fb-4f7b-4a43-aca1-e4522e4c73b3"
                ),
                "selectielijstklasse": (
                    "https://selectielijst.openzaak.nl/api/v1/resultaten/2a4b189b-3b93-4a61-8217-2d71101a7609"
                ),
                "toelichting": "Afgehandeld",
                "archiefnominatie": "blijvend_bewaren",
            },
        )
        self.stdout.write(
            self.style.SUCCESS("Created resultaattype %s." % resultaattype["url"])
        )

        ztc_client.operation(
            operation_id="informatieobjecttype_publish",
            data={},
            uuid=uuid_from_url(informatieobjecttype["url"]),
        )
        ztc_client.operation(
            operation_id="zaaktype_publish",
            data={},
            uuid=uuid_from_url(zaaktype["url"]),
        )
