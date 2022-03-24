from io import StringIO

from django.core.files import File
from django.test import TestCase, override_settings

import requests_mock
from privates.test import temp_private_root
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.notifications.models import Notification
from archiefbeheercomponent.report.tests.factories import DestructionReportFactory
from archiefbeheercomponent.tests.utils import mock_service_oas_get

from ..models import DestructionList
from ..tasks import create_destruction_zaak
from .factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
    DestructionListReviewFactory,
)


@temp_private_root()
@requests_mock.Mocker()
class CreateZaakTaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Service.objects.create(
            label="Zaken API",
            api_type=APITypes.zrc,
            api_root="https://oz.nl/zaken/api/v1/",
            oas="https://oz.nl/zaken/api/v1/schema/openapi.json",
        )
        Service.objects.create(
            label="Documenten API",
            api_type=APITypes.drc,
            api_root="https://oz.nl/documenten/api/v1/",
            oas="https://oz.nl/documenten/api/v1/schema/openapi.json",
        )

    def _set_up_mocks(self, m):
        mock_service_oas_get(
            m,
            "https://oz.nl/zaken/api/v1/",
            "zrc",
            oas_url="https://oz.nl/zaken/api/v1/schema/openapi.json",
        )
        mock_service_oas_get(
            m,
            "https://oz.nl/documenten/api/v1/",
            "drc",
            oas_url="https://oz.nl/documenten/api/v1/schema/openapi.json",
        )
        m.post(
            "https://oz.nl/zaken/api/v1/zaken",
            json={
                "url": "https://oz.nl/zaken/api/v1/zaken/123",
                "identificatie": "ZAAK-0001",
            },
            status_code=201,
        )
        m.post(
            "https://oz.nl/documenten/api/v1/enkelvoudiginformatieobjecten",
            json={
                "url": "https://oz.nl/documenten/api/v1/enkelvoudiginformatieobjecten/123"
            },
            status_code=201,
        )
        m.post("https://oz.nl/zaken/api/v1/zaakinformatieobjecten", status_code=201)
        m.post("https://oz.nl/zaken/api/v1/resultaten", status_code=201)
        m.post("https://oz.nl/zaken/api/v1/statussen", status_code=201)

    def test_create_zaak_from_destruction_list(self, m):
        self._set_up_mocks(m)

        destruction_list = DestructionListFactory.create()
        DestructionReportFactory.create(destruction_list=destruction_list)

        create_destruction_zaak(destruction_list.id)

        # Can't refresh from database due to fsm field
        destruction_list = DestructionList.objects.get(id=destruction_list.id)
        self.assertEqual(
            "https://oz.nl/zaken/api/v1/zaken/123", destruction_list.zaak_url
        )

        history = m.request_history

        eio_post_calls = 0
        zio_post_calls = 0
        for call in history:
            if call.url == "https://oz.nl/zaken/api/v1/zaakinformatieobjecten":
                zio_post_calls += 1

            if (
                call.url
                == "https://oz.nl/documenten/api/v1/enkelvoudiginformatieobjecten"
            ):
                eio_post_calls += 1

        self.assertEqual(1, eio_post_calls)
        self.assertEqual(1, zio_post_calls)

    def test_create_zaak_with_review_documents(self, m):
        self._set_up_mocks(m)

        destruction_list = DestructionListFactory.create()
        DestructionReportFactory.create(destruction_list=destruction_list)

        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            additional_document=File(StringIO("Some test content"), name="test.txt"),
        )

        create_destruction_zaak(destruction_list.id)

        history = m.request_history

        eio_post_calls = 0
        zio_post_calls = 0
        for call in history:
            if call.url == "https://oz.nl/zaken/api/v1/zaakinformatieobjecten":
                zio_post_calls += 1

            if (
                call.url
                == "https://oz.nl/documenten/api/v1/enkelvoudiginformatieobjecten"
            ):
                eio_post_calls += 1

        self.assertEqual(2, eio_post_calls)
        self.assertEqual(2, zio_post_calls)

    @override_settings(LANGUAGE_CODE="en")
    def test_create_zaak_notifies_users(self, m):
        self._set_up_mocks(m)

        user1, user2, user3 = UserFactory.create_batch(3)

        destruction_list = DestructionListFactory.create(
            author=user1, name="Test Notifications"
        )
        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=user2
        )
        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=user3
        )
        DestructionReportFactory.create(destruction_list=destruction_list)

        create_destruction_zaak(destruction_list.id)

        notifications = Notification.objects.filter(destruction_list=destruction_list)

        self.assertEqual(3, notifications.count())
        self.assertEqual(1, notifications.filter(user=user1).count())
        self.assertEqual(1, notifications.filter(user=user2).count())
        self.assertEqual(1, notifications.filter(user=user3).count())

        for notification in notifications:
            self.assertEqual(
                'Destruction list "Test Notifications" is processed and '
                "the destruction report is available in case ZAAK-0001",
                notification.message,
            )
