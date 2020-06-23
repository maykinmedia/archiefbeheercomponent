from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from timeline_logger.models import TimelineLog
from zds_client.client import ClientError

from rma.notifications.models import Notification

from ..constants import ListItemStatus, ListStatus
from ..models import DestructionList, DestructionListItem
from ..tasks import complete_and_notify, process_destruction_list, process_list_item
from .factories import DestructionListFactory, DestructionListItemFactory


class ProcessListTests(TestCase):
    @patch("rma.destruction.tasks.chain")
    @patch("rma.destruction.tasks.complete_and_notify")
    @patch("rma.destruction.tasks.process_list_item")
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


class ProcessListItemTests(TestCase):
    @patch("rma.destruction.tasks.remove_zaak")
    @patch("rma.destruction.tasks.fetch_zaak", return_value={"identificatie": "foobar"})
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
        "rma.destruction.tasks.remove_zaak",
        side_effect=ClientError("something went wrong"),
    )
    @patch("rma.destruction.tasks.fetch_zaak", return_value={"identificatie": "foobar"})
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
        self.assertEqual(notification.message, "Destruction list has been processed")
