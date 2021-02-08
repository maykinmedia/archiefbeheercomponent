from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils.translation import gettext as _

from timeline_logger.models import TimelineLog
from zds_client.client import ClientError

from archiefvernietigingscomponent.notifications.models import Notification

from ..constants import ListItemStatus, ListStatus
from ..models import DestructionList, DestructionListItem
from ..tasks import (
    complete_and_notify,
    process_destruction_list,
    process_list_item,
    update_zaak_from_list_item,
    update_zaken,
)
from ..utils import create_destruction_report
from .factories import (
    DestructionListFactory,
    DestructionListItemFactory,
    DestructionListItemReviewFactory,
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
        },
    )
    def test_process_list_item(self, mock_fetch_zaak, mock_remove_zaken):
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
        },
    )
    def test_process_list_item_fail(self, mock_fetch_zaak, mock_remove_zaken):
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
    @patch("archiefvernietigingscomponent.destruction.tasks.fetch_zaak")
    def test_process_list_item_status_update_processing(
        self, mock_fetch_zaak, mock_remove_zaken
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


class NotifyTests(TestCase):
    def test_complete_and_notify(self):
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


class DestructionReportTests(TestCase):
    def test_destruction_report_generation(self):
        destruction_list = DestructionListFactory.create()
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
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
            },
        )

        report = create_destruction_report(destruction_list)

        self.assertIn("<td>ZAAK-1</td>", report)
        self.assertIn("<td>Een zaak</td>", report)
        self.assertIn("<td>366 days</td>", report)

        self.assertIn("<td>ZAAK-2</td>", report)
        self.assertIn("<td>Een andere zaak</td>", report)
        self.assertIn("<td>394 days</td>", report)

    def test_failed_destruction_not_in_report(self):
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list, status=ListItemStatus.failed,
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
            },
        )

        report = create_destruction_report(destruction_list)

        self.assertNotIn("<td>ZAAK-1</td>", report)
        self.assertNotIn("<td>Een zaak</td>", report)
        self.assertNotIn("<td>366 days</td>", report)

        self.assertIn("<td>ZAAK-2</td>", report)
        self.assertIn("<td>Een andere zaak</td>", report)
        self.assertIn("<td>394 days</td>", report)


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
        self.assertEqual(log.template, "destruction/logs/item_update_succeeded.txt")

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
        self.assertEqual(log.template, "destruction/logs/item_update_failed.txt")

        mock_update_zaak.assert_called_once_with(list_item.zaak, archive_data, None)
