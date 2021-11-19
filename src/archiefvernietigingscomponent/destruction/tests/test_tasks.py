import datetime
from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

import requests_mock
from privates.test import temp_private_root
from timeline_logger.models import TimelineLog
from zds_client.client import ClientError
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from archiefvernietigingscomponent.notifications.models import Notification

from ...accounts.tests.factories import UserFactory
from ...constants import RoleTypeChoices
from ...emails.constants import EmailTypeChoices
from ...emails.models import EmailConfig
from ...emails.tests.factories import AutomaticEmailFactory
from ...report.models import DestructionReport
from ...tests.utils import mock_service_oas_get
from ..constants import ListItemStatus, ListStatus, ReviewStatus
from ..models import DestructionList, DestructionListItem
from ..tasks import (
    complete_and_notify,
    process_destruction_list,
    process_list_item,
    send_email_after_time,
    update_zaak_from_list_item,
    update_zaken,
)
from .factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
    DestructionListItemFactory,
    DestructionListItemReviewFactory,
    DestructionListReviewFactory,
)


@patch("archiefvernietigingscomponent.destruction.tasks.chain")
@patch("archiefvernietigingscomponent.destruction.tasks.complete_and_notify")
@patch("archiefvernietigingscomponent.destruction.tasks.process_list_item")
class ProcessListTests(TestCase):
    def test_process_list(self, mock_task_item, mock_notify, mock_chain):
        destruction_list = DestructionListFactory.create()
        list_items = DestructionListItemFactory.create_batch(
            5, destruction_list=destruction_list
        )

        process_destruction_list(destruction_list.id)

        # can't use refresh_from_db() because of django-fsm
        destruction_list = DestructionList.objects.get(id=destruction_list.id)
        self.assertEqual(destruction_list.status, ListStatus.processing)

        list_items_ids = [(list_item.id,) for list_item in list_items]

        mock_chain.assert_called_once_with(
            mock_task_item.chunks(list_items_ids, settings.ZAKEN_PER_TASK).group(),
            mock_notify.si(destruction_list.id),
        )

    def test_process_list_with_removed_items(
        self, mock_task_item, mock_notify, mock_chain
    ):
        destruction_list = DestructionListFactory.create()
        list_item_1, list_item_2 = DestructionListItemFactory.create_batch(
            2, destruction_list=destruction_list
        )
        list_item_1.remove()
        list_item_1.save()

        process_destruction_list(destruction_list.id)

        # can't use refresh_from_db() because of django-fsm
        destruction_list = DestructionList.objects.get(id=destruction_list.id)
        self.assertEqual(destruction_list.status, ListStatus.processing)

        list_items_ids = [(list_item_2.id,)]

        mock_chain.assert_called_once_with(
            mock_task_item.chunks(list_items_ids, settings.ZAKEN_PER_TASK).group(),
            mock_notify.si(destruction_list.id),
        )


class ProcessListItemTests(TestCase):
    @patch("archiefvernietigingscomponent.destruction.tasks.remove_zaak")
    @patch(
        "archiefvernietigingscomponent.destruction.tasks.fetch_zaak",
        return_value={
            "identificatie": "foobar",
            "omschrijving": "Een zaak",
            "toelichting": "Bah",
            "startdatum": "2020-01-01",
            "einddatum": "2021-01-01",
            "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
            "resultaat": "https://oz.nl/zaken/api/v1/resultaat/uuid-1",
            "verantwoordelijkeOrganisatie": "Some organisation",
        },
    )
    @patch(
        "archiefvernietigingscomponent.destruction.service.get_resultaat",
        return_value={
            "resultaattype": {
                "omschrijving": "Nice result type",
                "archiefactietermijn": "20 days",
            },
        },
    )
    def test_process_list_item(
        self, mock_fetch_zaak, mock_remove_zaken, mock_get_resultaat
    ):
        list_item = DestructionListItemFactory.create()

        process_list_item(list_item.id)

        # can't use refresh_from_db() because of django-fsm
        list_item = DestructionListItem.objects.get(id=list_item.id)
        self.assertEqual(list_item.status, ListItemStatus.destroyed)

        log = TimelineLog.objects.get()

        self.assertEqual(log.content_object, list_item)
        self.assertEqual(log.extra_data, {"zaak": "foobar"})

        mock_remove_zaken.assert_called_once_with(list_item.zaak)

    @patch(
        "archiefvernietigingscomponent.destruction.tasks.remove_zaak",
        side_effect=ClientError("something went wrong"),
    )
    @patch(
        "archiefvernietigingscomponent.destruction.tasks.fetch_zaak",
        return_value={
            "identificatie": "foobar",
            "omschrijving": "Een zaak",
            "toelichting": "Bah",
            "startdatum": "2020-01-01",
            "einddatum": "2021-01-01",
            "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
            "resultaat": "https://oz.nl/zaken/api/v1/resultaat/uuid-1",
            "verantwoordelijkeOrganisatie": "Some organisation",
        },
    )
    @patch("archiefvernietigingscomponent.destruction.service.get_resultaat")
    def test_process_list_item_fail(
        self, mock_fetch_zaak, mock_remove_zaken, mock_get_resultaat
    ):
        list_item = DestructionListItemFactory.create()

        process_list_item(list_item.id)

        # can't use refresh_from_db() because of django-fsm
        list_item = DestructionListItem.objects.get(id=list_item.id)
        self.assertEqual(list_item.status, ListItemStatus.failed)

        log = TimelineLog.objects.get()

        self.assertEqual(log.content_object, list_item)
        extra_data = log.extra_data
        self.assertEqual(extra_data["zaak"], "foobar")
        self.assertTrue("something went wrong" in extra_data["error"])

        mock_remove_zaken.assert_called_once_with(list_item.zaak)

    @patch("archiefvernietigingscomponent.destruction.tasks.remove_zaak")
    @patch(
        "archiefvernietigingscomponent.destruction.tasks.fetch_zaak",
        return_value={
            "identificatie": "foobar",
            "omschrijving": "Een zaak",
            "toelichting": "Bah",
            "startdatum": "2020-01-01",
            "einddatum": "2021-01-01",
            "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
            "resultaat": "https://oz.nl/zaken/api/v1/resultaat/uuid-1",
            "verantwoordelijkeOrganisatie": "Some organisation",
        },
    )
    @patch(
        "archiefvernietigingscomponent.destruction.service.get_resultaat",
        return_value={
            "resultaattype": {
                "omschrijving": "Nice result type",
                "archiefactietermijn": "20 days",
            },
        },
    )
    def test_process_list_item_status_update_processing(
        self, mock_fetch_zaak, mock_remove_zaken, mock_get_resultaat
    ):
        """
        Test that the db state is updated.
        """
        list_item = DestructionListItemFactory.create()

        def assert_list_item_status(url: str):
            # hook into mock call to make the assertion
            _list_item = DestructionListItem.objects.get(pk=list_item.pk)
            self.assertEqual(_list_item.status, ListItemStatus.processing)
            return {
                "identificatie": "foobar",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
            }

        mock_fetch_zaak.side_effect = assert_list_item_status

        process_list_item(list_item.id)

    @patch(
        "archiefvernietigingscomponent.destruction.tasks.fetch_zaak",
        side_effect=ClientError("Oopsiewoopsie"),
    )
    def test_process_list_item_fetch_zaak_fail_recorded(self, mock_fetch_zaak):
        list_item = DestructionListItemFactory.create()

        process_list_item(list_item.id)

        list_item = DestructionListItem.objects.get(pk=list_item.pk)
        self.assertEqual(list_item.status, ListItemStatus.failed)

    @patch(
        "archiefvernietigingscomponent.destruction.tasks.fetch_zaak",
        return_value={
            "identificatie": "foobar",
            "omschrijving": "Een zaak",
            "toelichting": "Bah",
            "startdatum": "2020-01-01",
            "einddatum": "2021-01-01",
            "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
            "resultaat": "https://oz.nl/zaken/api/v1/resultaat/uuid-1",
            "verantwoordelijkeOrganisatie": "Some organisation",
        },
    )
    @patch("archiefvernietigingscomponent.destruction.tasks.remove_zaak")
    @patch(
        "archiefvernietigingscomponent.destruction.service.get_resultaat",
        return_value={
            "resultaattype": {
                "omschrijving": "Nice result type",
                "archiefactietermijn": "20 days",
            },
        },
    )
    @override_settings(AVC_DEMO_MODE=True)
    def test_zaak_not_removed_in_demo_mode(
        self, mock_fetch_zaak, mock_remove_zaken, mock_get_resultaat
    ):
        list_item = DestructionListItemFactory.create()

        process_list_item(list_item.id)

        # can't use refresh_from_db() because of django-fsm
        list_item = DestructionListItem.objects.get(id=list_item.id)
        self.assertEqual(list_item.status, ListItemStatus.destroyed)

        log = TimelineLog.objects.get()

        self.assertEqual(log.content_object, list_item)
        self.assertEqual(log.extra_data, {"zaak": "foobar"})

        mock_remove_zaken.assert_not_called()


@requests_mock.Mocker()
@temp_private_root()
@override_settings(LANGUAGE_CODE="en")
class NotifyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        Service.objects.create(
            label="Catalogi API",
            api_type=APITypes.ztc,
            api_root="https://oz.nl/catalogi/api/v1",
            oas="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )

    @patch.object(timezone, "now", return_value=datetime.datetime(2021, 11, 1, 00))
    def time_past(self, m):
        return timezone.make_aware(timezone.now())

    def test_email_when_delayed(self, m):
        AutomaticEmailFactory.create(type=EmailTypeChoices.update_required)
        time_past = self.time_past()
        destruction_list = DestructionListFactory.create()
        assignees = DestructionListAssigneeFactory.create_batch(
            size=2, destruction_list=destruction_list
        )
        assignees[0].assigned_on = time_past
        destruction_list.save()
        assignees[0].save()
        send_email_after_time(destruction_list.id)
        self.assertEqual(len(mail.outbox), 1)

    def test_complete_and_notify(self, m):
        destruction_list = DestructionListFactory.create()
        destruction_list.process()
        destruction_list.save()

        complete_and_notify(destruction_list.id)

        # can't use refresh_from_db() because of django-fsm
        destruction_list = DestructionList.objects.get(id=destruction_list.id)
        self.assertEqual(destruction_list.status, ListStatus.completed)

        notification = Notification.objects.get()

        self.assertEqual(notification.destruction_list, destruction_list)
        self.assertEqual(notification.user, destruction_list.author)
        self.assertEqual(notification.message, _("Processing of the list is complete."))

    def test_complete_and_notify_process_owner(self, m):
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(name="Summer List",)
        DestructionListReviewFactory.create(
            author=process_owner,
            status=ReviewStatus.approved,
            destruction_list=destruction_list,
        )

        destruction_list.process()
        destruction_list.save()

        complete_and_notify(destruction_list.id)

        notifications = Notification.objects.all()

        self.assertEqual(2, notifications.count())

        notification = notifications.get(user=process_owner)

        self.assertEqual(notification.destruction_list, destruction_list)

        report = DestructionReport.objects.get()

        self.assertEqual(
            notification.message,
            _(
                "Destruction list %(list)s has been processed. "
                "You can download the report of destruction here: %(url)s"
            )
            % {
                "list": "Summer List",
                "url": "http://example.com{}".format(
                    reverse("report:download-report", args=[report.pk])
                ),
            },
        )

        self.client.force_login(process_owner)

        response_pdf = self.client.get(
            reverse("report:download-report", args=[report.pk]), data={"type": "pdf"}
        )
        response_csv = self.client.get(
            reverse("report:download-report", args=[report.pk]), data={"type": "csv"}
        )

        self.assertEqual(200, response_pdf.status_code)
        self.assertGreater(len(response_pdf.content), 0)
        self.assertEqual(200, response_csv.status_code)
        self.assertGreater(len(response_csv.content), 0)

    def test_all_deleted_cases_are_in_destruction_report(self, m):
        config = EmailConfig.get_solo()
        config.municipality = "Example"
        config.from_email = "email@test.avc"
        config.save()

        AutomaticEmailFactory.create(
            type=EmailTypeChoices.report_available,
            body="Report is available!",
            subject="Report",
        )

        archivaris = UserFactory.create(
            role__type=RoleTypeChoices.archivist,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )

        destruction_list = DestructionListFactory.create(
            status=ListStatus.processing,
            name="Nice list",
            created=timezone.make_aware(datetime.datetime(2021, 2, 15, 10, 30)),
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
                "verantwoordelijke_organisatie": "Nice organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nice result type",
                        "archiefactietermijn": "20 days",
                    }
                },
                "relevante_andere_zaken": [],
            },
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-2",
                "omschrijving": "Een andere zaak",
                "toelichting": "",
                "startdatum": "2020-02-01",
                "einddatum": "2021-03-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
                "verantwoordelijke_organisatie": "Nicer organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nicer result type",
                        "archiefactietermijn": "40 days",
                    }
                },
                "relevante_andere_zaken": [{"url": "http://some.zaak"}],
            },
        )
        DestructionListReviewFactory.create(
            author=archivaris,
            status=ReviewStatus.approved,
            destruction_list=destruction_list,
        )
        mock_service_oas_get(
            m,
            "https://oz.nl/catalogi/api/v1",
            "ztc",
            oas_url="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1", json={},
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2", json={},
        )

        complete_and_notify(destruction_list.id)

        self.assertEqual(1, len(mail.outbox))

        sent_mail = mail.outbox[0]

        self.assertEqual("Report", sent_mail.subject)
        self.assertEqual("email@test.avc", sent_mail.from_email)
        self.assertIn(archivaris.email, sent_mail.to)
        self.assertEqual(
            "Report is available!", sent_mail.body,
        )

    def test_no_email_sent_if_no_cases_deleted(self, m):
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list, status=ListItemStatus.failed,
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, status=ListItemStatus.failed,
        )

        complete_and_notify(destruction_list.id)

        self.assertEqual(0, len(mail.outbox))

    def test_no_email_sent_if_no_archivaris_assigned(self, m):
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
                "verantwoordelijke_organisatie": "Nicer organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nicer result type",
                        "archiefactietermijn": "40 days",
                    }
                },
                "relevante_andere_zaken": [{"url": "http://some.zaak"}],
            },
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-2",
                "omschrijving": "Een andere zaak",
                "toelichting": "",
                "startdatum": "2020-02-01",
                "einddatum": "2021-03-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
                "verantwoordelijke_organisatie": "Nicer organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nicer result type",
                        "archiefactietermijn": "40 days",
                    }
                },
                "relevante_andere_zaken": [{"url": "http://some.zaak"}],
            },
        )
        mock_service_oas_get(
            m,
            "https://oz.nl/catalogi/api/v1",
            "ztc",
            oas_url="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1", json={},
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2", json={},
        )

        complete_and_notify(destruction_list.id)

        self.assertEqual(0, len(mail.outbox))


@patch(
    "archiefvernietigingscomponent.destruction.tasks.update_zaak_from_list_item.chunks"
)
class UpdateZakenTests(TestCase):
    def test_update_zaken(self, mock_update_zaak):
        destruction_list = DestructionListFactory.create()
        list_items = DestructionListItemFactory.create_batch(
            3, destruction_list=destruction_list, status=ListItemStatus.removed
        )
        archive_data = {
            "archiefnominatie": "blijvend_bewaren",
            "archiefactiedatum": "2020-06-17",
        }
        data = [[list_item.id, archive_data] for list_item in list_items]

        update_zaken(data)

        mock_update_zaak.assert_called_once_with(data, settings.ZAKEN_PER_TASK)


class UpdateZaakTests(TestCase):
    @patch(
        "archiefvernietigingscomponent.destruction.tasks.update_zaak",
        return_value={"identificatie": "foobar"},
    )
    def test_update_zaak_from_list_item(self, mock_update_zaak):
        list_item = DestructionListItemFactory.create(status=ListItemStatus.removed)
        DestructionListItemReviewFactory.create(
            destruction_list_item=list_item, text="Change archive params"
        )
        archive_data = {
            "archiefnominatie": "blijvend_bewaren",
            "archiefactiedatum": "2020-06-17",
        }

        update_zaak_from_list_item(list_item.id, archive_data)

        log = TimelineLog.objects.get()
        self.assertEqual(log.content_object, list_item)
        self.assertEqual(log.extra_data, {"zaak": "foobar"})
        self.assertEqual(log.template, "destruction/logs/item_update_succeeded.html")

        mock_update_zaak.assert_called_once_with(
            list_item.zaak, archive_data, "Change archive params"
        )

    @patch(
        "archiefvernietigingscomponent.destruction.tasks.update_zaak",
        side_effect=ClientError("something went wrong"),
    )
    def test_update_zaak_from_list_item_fail(self, mock_update_zaak):
        list_item = DestructionListItemFactory.create(status=ListItemStatus.removed)
        archive_data = {
            "archiefnominatie": "blijvend_bewaren",
            "archiefactiedatum": "2020-06-17",
        }

        update_zaak_from_list_item(list_item.id, archive_data)

        log = TimelineLog.objects.get()
        self.assertEqual(log.content_object, list_item)
        extra_data = log.extra_data
        self.assertEqual(extra_data["zaak"], None)
        self.assertTrue("something went wrong" in extra_data["error"])
        self.assertEqual(log.template, "destruction/logs/item_update_failed.html")

        mock_update_zaak.assert_called_once_with(list_item.zaak, archive_data, None)
