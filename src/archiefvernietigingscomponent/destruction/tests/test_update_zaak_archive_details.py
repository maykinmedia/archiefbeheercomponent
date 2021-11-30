from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from django_webtest import WebTest
from furl import furl
from zds_client.client import ClientError

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory

from ..constants import ZaakArchiefnominatieChoices


class UpdateZaakArchiveDetailsTests(WebTest):
    def test_cant_access_without_can_start_destruction(self):
        user = UserFactory(role__can_start_destruction=False)
        self.client.force_login(user)

        response = self.client.get(reverse("destruction:update-zaak-archive-details"))

        self.assertEqual(403, response.status_code)

    def test_can_access_with_can_start_destruction(self):
        user = UserFactory(role__can_start_destruction=True)
        self.client.force_login(user)

        response = self.client.get(reverse("destruction:update-zaak-archive-details"))

        self.assertEqual(200, response.status_code)

    def test_wrong_query_params_displays_empty_form(self):
        user = UserFactory(role__can_start_destruction=True)
        view_url = furl(reverse("destruction:update-zaak-archive-details"))
        view_url.args["url"] = "an-invalid-url"

        response = self.app.get(view_url.url, user=user)

        self.assertEqual(200, response.status_code)

        form = response.form

        self.assertEqual("", form["url"].value)

    def test_fill_initial_data_with_query_params(self):
        user = UserFactory(role__can_start_destruction=True)
        view_url = furl(reverse("destruction:update-zaak-archive-details"))
        view_url.args["url"] = "http://openzaak.nl/some/valid/zaak/url"
        view_url.args["archiefnominatie"] = ZaakArchiefnominatieChoices.blijvend_bewaren

        response = self.app.get(view_url.url, user=user)

        self.assertEqual(200, response.status_code)

        form = response.form

        self.assertEqual("http://openzaak.nl/some/valid/zaak/url", form["url"].value)
        self.assertEqual(
            ZaakArchiefnominatieChoices.blijvend_bewaren, form["archiefnominatie"].value
        )

    @patch("archiefvernietigingscomponent.destruction.views.update_zaak",)
    def test_submit_successful_form_redirects(self, m_update_zaak):
        user = UserFactory(role__can_start_destruction=True)
        view_url = furl(reverse("destruction:update-zaak-archive-details"))

        form = self.app.get(view_url.url, user=user).form

        form["url"] = "http://openzaak.nl/some/valid/zaak/url"
        form["archiefnominatie"] = ZaakArchiefnominatieChoices.blijvend_bewaren
        form["archiefactiedatum_day"] = "1"
        form["archiefactiedatum_month"] = "1"
        form["archiefactiedatum_year"] = "2021"
        form["comment"] = "Some interesting comment"

        response = form.submit()

        self.assertRedirects(
            response, reverse("destruction:zaken-without-archive-date")
        )
        m_update_zaak.assert_called_with(
            "http://openzaak.nl/some/valid/zaak/url",
            {
                "archiefnominatie": ZaakArchiefnominatieChoices.blijvend_bewaren,
                "archiefactiedatum": "2021-01-01",
            },
            audit_comment="Some interesting comment",
        )

    @patch(
        "archiefvernietigingscomponent.destruction.views.update_zaak",
        side_effect=ClientError,
    )
    @override_settings(LANGUAGE_CODE="en")
    def test_client_error_during_update(self, m_update_zaak):
        user = UserFactory(role__can_start_destruction=True)
        view_url = furl(reverse("destruction:update-zaak-archive-details"))

        form = self.app.get(view_url.url, user=user).form

        form["url"] = "http://openzaak.nl/some/valid/zaak/url"
        form["archiefnominatie"] = ZaakArchiefnominatieChoices.blijvend_bewaren
        form["archiefactiedatum_day"] = "1"
        form["archiefactiedatum_month"] = "1"
        form["archiefactiedatum_year"] = "2021"
        form["comment"] = "Some interesting comment"

        response = form.submit()

        self.assertEqual(200, response.status_code)
        self.assertContains(
            response, "An error has occurred. The case could not be updated."
        )

    @patch("archiefvernietigingscomponent.destruction.views.update_zaak",)
    def test_empty_archiefactiedatum(self, m_update_zaak):
        user = UserFactory(role__can_start_destruction=True)
        view_url = furl(reverse("destruction:update-zaak-archive-details"))

        form = self.app.get(view_url.url, user=user).form

        form["url"] = "http://openzaak.nl/some/valid/zaak/url"
        form["archiefnominatie"] = ZaakArchiefnominatieChoices.blijvend_bewaren
        form["comment"] = "Some interesting comment"

        response = form.submit()

        self.assertRedirects(
            response, reverse("destruction:zaken-without-archive-date")
        )
        m_update_zaak.assert_called_with(
            "http://openzaak.nl/some/valid/zaak/url",
            {"archiefnominatie": ZaakArchiefnominatieChoices.blijvend_bewaren},
            audit_comment="Some interesting comment",
        )
