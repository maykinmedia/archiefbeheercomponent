from django.urls import reverse

from django_webtest import WebTest

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory

from ..models import ArchiveConfig


class ArchiefConfiguratieTest(WebTest):
    def test_create_zaak_set_but_misconfigured(self):
        user = UserFactory.create(is_staff=True, is_superuser=True)
        response = self.app.get(
            reverse("admin:destruction_archiveconfig_change"), user=user
        )
        form = response.form
        form["create_zaak"] = True

        response = form.submit()

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "form-row errors field-create_zaak")

    def test_create_zaak_set(self):
        user = UserFactory.create(is_staff=True, is_superuser=True)
        response = self.app.get(
            reverse("admin:destruction_archiveconfig_change"), user=user
        )
        form = response.form
        form["create_zaak"] = True
        form["source_organisation"] = "111222333"
        form["case_type"] = "http://openzaak.nl/zaaktype/1"
        form["status_type"] = "http://openzaak.nl/statustype/1"
        form["result_type"] = "http://openzaak.nl/resultaattype/1"
        form["document_type"] = "http://openzaak.nl/informatieobjecttype/1"

        response = form.submit().follow()

        self.assertEqual(200, response.status_code)

        conf = ArchiveConfig.get_solo()

        self.assertEqual(conf.create_zaak, True)
        self.assertEqual(conf.source_organisation, "111222333")
        self.assertEqual(conf.case_type, "http://openzaak.nl/zaaktype/1")
        self.assertEqual(conf.result_type, "http://openzaak.nl/resultaattype/1")
        self.assertEqual(conf.status_type, "http://openzaak.nl/statustype/1")
        self.assertEqual(
            conf.document_type, "http://openzaak.nl/informatieobjecttype/1"
        )

    def test_no_zaak_created_no_report_downloadable(self):
        user = UserFactory.create(is_staff=True, is_superuser=True)
        response = self.app.get(
            reverse("admin:destruction_archiveconfig_change"), user=user
        )
        form = response.form
        form["create_zaak"] = False
        form["destruction_report_downloadable"] = False

        response = form.submit()

        self.assertEqual(200, response.status_code)
        self.assertContains(
            response, "form-row errors field-destruction_report_downloadable"
        )
