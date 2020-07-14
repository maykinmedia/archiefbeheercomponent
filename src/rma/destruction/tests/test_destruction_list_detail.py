from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from django_capture_on_commit_callbacks import capture_on_commit_callbacks
from timeline_logger.models import TimelineLog

from rma.accounts.tests.factories import UserFactory
from rma.notifications.models import Notification

from ..constants import ListItemStatus, Suggestion
from ..models import DestructionList, DestructionListItem
from .factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
    DestructionListItemFactory,
    DestructionListReviewFactory,
)

MANAGEMENT_FORM_DATA = {
    "items-TOTAL_FORMS": 3,
    "items-INITIAL_FORMS": 3,
    "items-MIN_NUM_FORMS": 0,
    "items-MAX_NUM_FORMS": 1000,
}


class DestructionListDetailTests(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.user = UserFactory(role__can_start_destruction=True)
        self.client.force_login(self.user)

    @patch("rma.destruction.views.update_zaken.delay")
    def test_update_destruction_list(self, m):
        destruction_list = DestructionListFactory.create(
            author=self.user, assignee=self.user
        )
        list_items = DestructionListItemFactory.create_batch(
            3, destruction_list=destruction_list
        )
        assignee = DestructionListAssigneeFactory.create(
            destruction_list=destruction_list
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list, author=assignee.assignee
        )

        url = reverse("destruction:record-manager-detail", args=[destruction_list.id])
        data = {
            "items-0-id": list_items[0].id,
            "items-0-action": Suggestion.change_and_remove,
            "items-0-archiefnominatie": "blijvend_bewaren",
            "items-0-archiefactiedatum": "2020-06-17",
            "items-1-id": list_items[1].id,
            "items-1-action": Suggestion.remove,
            "items-1-archiefnominatie": "vernietigen",
            "items-1-archiefactiedatum": "2020-06-16",
            "items-2-id": list_items[2].id,
            "items-2-action": "",
            "items-2-archiefnominatie": "vernietigen",
            "items-2-archiefactiedatum": "2020-06-15",
        }
        data.update(MANAGEMENT_FORM_DATA)

        with capture_on_commit_callbacks(execute=True) as callbacks:
            response = self.client.post(url, data=data)

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        # can't refresh_from_db because of fsm protection
        destruction_list = DestructionList.objects.get(id=destruction_list.id)

        # check items statuses
        for item in list_items[0:2]:
            list_item = DestructionListItem.objects.get(id=item.id)
            self.assertEqual(list_item.status, ListItemStatus.removed)

        last_item = DestructionListItem.objects.get(id=list_items[2].id)
        self.assertEqual(last_item.status, ListItemStatus.suggested)

        # check assignee
        self.assertEqual(destruction_list.assignee, assignee.assignee)

        # check log
        timeline_log = TimelineLog.objects.get()
        self.assertEqual(timeline_log.user, self.user)
        self.assertEqual(timeline_log.template, "destruction/logs/updated.txt")

        # check notification
        notification = Notification.objects.get()
        self.assertEqual(notification.user, assignee.assignee)
        self.assertEqual(notification.destruction_list, destruction_list)
        self.assertEqual(
            notification.message, "You are assigned to the destruction list"
        )

        # check starting update task
        self.assertEqual(len(callbacks), 1)
        m.assert_called_once_with(
            [
                (
                    list_items[0].id,
                    {
                        "archiefnominatie": "blijvend_bewaren",
                        "archiefactiedatum": "2020-06-17",
                    },
                )
            ]
        )
