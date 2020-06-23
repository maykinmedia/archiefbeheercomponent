from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from rma.accounts.tests.factories import UserFactory

from ..constants import ListItemStatus, ListStatus
from ..models import DestructionList


class CreateDestructionListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(role__can_start_destruction=True)

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    @patch("rma.destruction.forms.transaction.on_commit")
    def test_create_list(self, m):
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

        # transactoin.on_commit
        m.assert_called_once()
