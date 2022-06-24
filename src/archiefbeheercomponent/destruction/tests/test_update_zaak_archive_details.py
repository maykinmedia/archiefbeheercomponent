from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from django_webtest import WebTest
from furl import furl
from zds_client.client import ClientError

from archiefbeheercomponent.accounts.tests.factories import UserFactory

from ..constants import Archiefnominatie, Archiefstatus


class UpdateZaakArchiveDetailsTests(WebTest):
    def test_cant_access_without_can_start_destruction(self):
        user = UserFactory(role__can_start_destruction=False)
        self.client.force_login(user)

        response = self.client.get(reverse("destruction:update-zaak-archive-details"))

        self.assertEqual(403, response.status_code)

    def test_permission_denied_if_no_zaak_url(self):
        user = UserFactory(role__can_start_destruction=True)
        self.client.force_login(user)

        response = self.client.get(reverse("destruction:update-zaak-archive-details"))

        self.assertEqual(403, response.status_code)

    @patch("archiefbeheercomponent.destruction.views.record_manager.fetch_zaak")
    def test_can_access_with_can_start_destruction_and_zaak_url(self, m_fetch_zaak):
        user = UserFactory(role__can_start_destruction=True)
        self.client.force_login(user)

        form_url = furl(reverse("destruction:update-zaak-archive-details"))
        form_url.args.set("url", "http://openzaak.nl/some/zaak")

        response = self.client.get(form_url.url)

        self.assertEqual(200, response.status_code)

    @patch(
        "archiefbeheercomponent.destruction.views.record_manager.fetch_zaak",
        return_value={
            "url": "http://openzaak.nl/some/valid/zaak/url",
            "identificatie": "ZAAK-1",
            "archiefnominatie": "blijvend_bewaren",
            "archiefstatus": "nog_te_archiveren",
            "archiefactiedatum": "2030-02-01",
        },
    )
    def test_fill_initial_data(self, m_fetch_zaak):
        user = UserFactory(role__can_start_destruction=True)
        view_url = furl(reverse("destruction:update-zaak-archive-details"))
        view_url.args["url"] = "http://openzaak.nl/some/valid/zaak/url"

        response = self.app.get(view_url.url, user=user)

        self.assertEqual(200, response.status_code)

        form = response.form

        self.assertEqual("http://openzaak.nl/some/valid/zaak/url", form["url"].value)
        self.assertEqual(
            Archiefnominatie.blijvend_bewaren, form["archiefnominatie"].value
        )
        self.assertEqual(Archiefstatus.nog_te_archiveren, form["archiefstatus"].value)
        self.assertEqual("1", form["archiefactiedatum_day"].value)
        self.assertEqual("2", form["archiefactiedatum_month"].value)
        self.assertEqual("2030", form["archiefactiedatum_year"].value)

    @patch(
        "archiefbeheercomponent.destruction.views.record_manager.fetch_zaak",
        return_value={"url": "http://openzaak.nl/some/zaak"},
    )
    @patch(
        "archiefbeheercomponent.destruction.views.record_manager.update_zaak",
    )
    def test_submit_successful_form_redirects(self, m_update_zaak, m_fetch_zaak):
        user = UserFactory(role__can_start_destruction=True)
        view_url = furl(reverse("destruction:update-zaak-archive-details"))
        view_url.args.set("url", "http://openzaak.nl/some/zaak")

        form = self.app.get(view_url.url, user=user).form

        form["url"] = "http://openzaak.nl/some/valid/zaak/url"
        form["archiefnominatie"] = Archiefnominatie.blijvend_bewaren
        form["archiefactiedatum_day"] = "1"
        form["archiefactiedatum_month"] = "1"
        form["archiefactiedatum_year"] = "2030"
        form["archiefstatus"] = Archiefstatus.nog_te_archiveren
        form["comment"] = "Some interesting comment"

        response = form.submit()

        self.assertRedirects(response, view_url.url, fetch_redirect_response=False)
        m_update_zaak.assert_called_with(
            "http://openzaak.nl/some/valid/zaak/url",
            {
                "archiefnominatie": Archiefnominatie.blijvend_bewaren,
                "archiefstatus": Archiefstatus.nog_te_archiveren,
                "archiefactiedatum": "2030-01-01",
            },
            audit_comment="Some interesting comment",
        )

        response = response.follow()
        messages = list(response.context.get("messages"))

        self.assertEqual(1, len(messages))
        self.assertEqual(messages[0].tags, "success")

    @patch("archiefbeheercomponent.destruction.views.record_manager.fetch_zaak")
    @patch(
        "archiefbeheercomponent.destruction.views.record_manager.update_zaak",
        side_effect=ClientError(
            {
                "type": "http://127.0.0.1:8123/ref/fouten/ValidationError/",
                "code": "invalid",
                "title": "Invalid input.",
                "status": 400,
                "detail": "",
                "instance": "urn:uuid:c8d9bf6b-4469-4b93-8411-1ebb5e4f4a40",
                "invalidParams": [
                    {
                        "name": "nonFieldErrors",
                        "code": "documents-not-archived",
                        "reason": "Some error message",
                    }
                ],
            }
        ),
    )
    @override_settings(LANGUAGE_CODE="en")
    def test_client_error_during_update(self, m_update_zaak, m_fetch_zaak):
        user = UserFactory(role__can_start_destruction=True)
        view_url = furl(reverse("destruction:update-zaak-archive-details"))
        view_url.args.set("url", "http://openzaak.nl/some/zaak")

        form = self.app.get(view_url.url, user=user).form

        form["url"] = "http://openzaak.nl/some/valid/zaak/url"
        form["archiefnominatie"] = Archiefnominatie.blijvend_bewaren
        form["archiefactiedatum_day"] = "1"
        form["archiefactiedatum_month"] = "1"
        form["archiefactiedatum_year"] = "2030"
        form["comment"] = "Some interesting comment"

        response = form.submit()

        self.assertEqual(200, response.status_code)
        self.assertContains(
            response, "An error has occurred. The case could not be updated."
        )
        self.assertContains(
            response,
            "Some error message",
        )

    @patch(
        "archiefbeheercomponent.destruction.views.record_manager.fetch_zaak",
        return_value={"url": "http://openzaak.nl/some/zaak"},
    )
    @patch(
        "archiefbeheercomponent.destruction.views.record_manager.update_zaak",
    )
    def test_empty_archiefactiedatum(self, m_update_zaak, m_fetch_zaak):
        user = UserFactory(role__can_start_destruction=True)
        view_url = furl(reverse("destruction:update-zaak-archive-details"))
        view_url.args.set("url", "http://openzaak.nl/some/zaak")

        form = self.app.get(view_url.url, user=user).form

        form["url"] = "http://openzaak.nl/some/valid/zaak/url"
        form["archiefnominatie"] = Archiefnominatie.blijvend_bewaren
        form["comment"] = "Some interesting comment"

        response = form.submit()

        self.assertRedirects(response, view_url.url, fetch_redirect_response=False)
        m_update_zaak.assert_called_with(
            "http://openzaak.nl/some/valid/zaak/url",
            {"archiefnominatie": Archiefnominatie.blijvend_bewaren},
            audit_comment="Some interesting comment",
        )

        response = response.follow()
        messages = list(response.context.get("messages"))

        self.assertEqual(1, len(messages))
        self.assertEqual(messages[0].tags, "success")

    @patch("archiefbeheercomponent.destruction.views.record_manager.fetch_zaak")
    @patch(
        "archiefbeheercomponent.destruction.views.record_manager.update_zaak",
        side_effect=ClientError({"some_unexpected_keys": "some_unexpected_values"}),
    )
    @override_settings(LANGUAGE_CODE="en")
    def test_unexpected_client_error_format_does_not_cause_error(
        self, m_update_zaak, m_fetch_zaak
    ):
        user = UserFactory(role__can_start_destruction=True)
        view_url = furl(reverse("destruction:update-zaak-archive-details"))
        view_url.args.set("url", "http://openzaak.nl/some/zaak")

        form = self.app.get(view_url.url, user=user).form

        form["url"] = "http://openzaak.nl/some/valid/zaak/url"
        form["archiefnominatie"] = Archiefnominatie.blijvend_bewaren
        form["archiefactiedatum_day"] = "1"
        form["archiefactiedatum_month"] = "1"
        form["archiefactiedatum_year"] = "2030"
        form["comment"] = "Some interesting comment"

        response = form.submit()

        self.assertEqual(200, response.status_code)
        self.assertContains(
            response, "An error has occurred. The case could not be updated."
        )
