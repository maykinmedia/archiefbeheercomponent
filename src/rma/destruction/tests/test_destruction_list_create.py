from django.test import TestCase
from django.urls import reverse

from rma.accounts.tests.factories import UserFactory
from rma.notifications.models import Notification

from ..constants import ListItemStatus, ListStatus
from ..models import DestructionList


class CreateDestructionListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(role__can_start_destruction=True)

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_create_list(self):
        reviewers = UserFactory.create_batch(2, role__can_review_destruction=True)
        zaken = [f"http://some.zaken.nl/api/v1/zaken/{i}" for i in range(1, 3)]

        url = reverse("destruction:record-manager-create")
        data = {
            "name": "test list",
            "zaken": ",".join(zaken),
            "reviewer_1": reviewers[0].id,
            "reviewer_2": reviewers[1].id,
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        destruction_list = DestructionList.objects.get()

        self.assertEqual(destruction_list.name, "test list")
        self.assertEqual(destruction_list.author, self.user)
        self.assertEqual(destruction_list.status, ListStatus.in_progress)
        self.assertEqual(destruction_list.items.count(), len(zaken))

        list_items = destruction_list.items.order_by("id").all()

        for i, list_item in enumerate(list_items):
            self.assertEqual(list_item.status, ListItemStatus.suggested)
            self.assertEqual(list_item.zaak, zaken[i])

        self.assertEqual(destruction_list.assignees.count(), len(reviewers))
        self.assertEqual(destruction_list.assignee, reviewers[0])

        list_assignees = destruction_list.assignees.order_by("id").all()

        for i, list_assignee in enumerate(list_assignees):
            self.assertEqual(list_assignee.assignee, reviewers[i])
            self.assertEqual(list_assignee.order, i + 1)

        # check that a log entry was created
        timeline_log = destruction_list.logs.get()
        self.assertEqual(timeline_log.user, self.user)
        self.assertEqual(timeline_log.template, "destruction/logs/created.txt")

        # check that notifications were sent
        notifications = Notification.objects.order_by("id").all()
        self.assertEqual(notifications.count(), 2)
        notif_create, notif_assign = notifications
        self.assertEqual(notif_create.user, destruction_list.author)
        self.assertEqual(notif_create.message, "Destruction list has been created")
        self.assertEqual(notif_assign.user, destruction_list.assignee)
        self.assertEqual(
            notif_assign.message, "You are assigned to the destruction list"
        )
