from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import gettext as _

from timeline_logger.models import TimelineLog

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.notifications.models import Notification

from ..constants import ListItemStatus, ListStatus
from ..models import ArchiveConfig, DestructionList


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
        zaken_identificaties = ["ZAAK-1", "ZAAK-2", "ZAAK-3"]

        url = reverse("destruction:record-manager-create")
        data = {
            "name": "test list",
            "zaken": ",".join(zaken),
            "reviewers": [str(reviewer.id) for reviewer in reviewers],
            "zaken_identificaties": ",".join(zaken_identificaties),
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
        self.assertEqual(timeline_log.template, "destruction/logs/created.html")

        # check that notifications were sent
        notification = Notification.objects.get()
        self.assertEqual(notification.user, destruction_list.assignee)
        self.assertEqual(notification.message, _("You are assigned for review."))

        logs = TimelineLog.objects.all()

        self.assertEqual(1, logs.count())

        log = logs.first()

        self.assertIn("items", log.extra_data)
        self.assertEqual(zaken_identificaties, sorted(log.extra_data["items"]))

    def test_list_with_short_review_process(self):
        archive_config = ArchiveConfig.get_solo()
        archive_config.short_review_zaaktypes = ["http://example.com/zaak/uuid-1"]
        archive_config.save()

        url = reverse("destruction:record-manager-create")

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertIn(
            b'<script id="short-review-zaaktypes" type="application/json">["http://example.com/zaak/uuid-1"]</script>',
            response.content,
        )

    def test_assigned_on_field_population_on_assignment(self):
        reviewers = UserFactory.create_batch(2, role__can_review_destruction=True)
        zaken = [f"http://some.zaken.nl/api/v1/zaken/{i}" for i in range(1, 3)]
        zaken_identificaties = ["ZAAK-1", "ZAAK-2", "ZAAK-3"]

        url = reverse("destruction:record-manager-create")
        data = {
            "name": "test list",
            "zaken": ",".join(zaken),
            "reviewers": [str(reviewer.id) for reviewer in reviewers],
            "zaken_identificaties": ",".join(zaken_identificaties),
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        destruction_list = DestructionList.objects.get()
        assignees = destruction_list.assignees.order_by("id")

        self.assertIsNotNone(assignees.first().assigned_on)
        self.assertIsNone(assignees.last().assigned_on)

    def test_can_have_more_than_2_assignees(self):
        reviewers = UserFactory.create_batch(3, role__can_review_destruction=True)
        zaken = [f"http://some.zaken.nl/api/v1/zaken/{i}" for i in range(1, 3)]
        zaken_identificaties = ["ZAAK-1", "ZAAK-2", "ZAAK-3"]

        url = reverse("destruction:record-manager-create")
        data = {
            "name": "test list",
            "zaken": ",".join(zaken),
            "reviewers": [str(reviewer.id) for reviewer in reviewers],
            "zaken_identificaties": ",".join(zaken_identificaties),
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        destruction_list = DestructionList.objects.get()
        assignees = destruction_list.assignees.order_by("id")

        self.assertEqual(3, assignees.count())

    def test_assignees_are_deduplicated(self):
        reviewer = UserFactory.create(role__can_review_destruction=True)
        zaken = [f"http://some.zaken.nl/api/v1/zaken/{i}" for i in range(1, 3)]
        zaken_identificaties = ["ZAAK-1", "ZAAK-2", "ZAAK-3"]

        url = reverse("destruction:record-manager-create")
        data = {
            "name": "test list",
            "zaken": ",".join(zaken),
            "reviewers": [reviewer.id, reviewer.id],
            "zaken_identificaties": ",".join(zaken_identificaties),
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        destruction_list = DestructionList.objects.get()
        assignees = destruction_list.assignees.order_by("id")

        self.assertEqual(1, assignees.count())

    @override_settings(LANGUAGE_CODE="en")
    def test_list_must_have_at_least_one_assignee(self):
        zaken = [f"http://some.zaken.nl/api/v1/zaken/{i}" for i in range(1, 3)]
        zaken_identificaties = ["ZAAK-1", "ZAAK-2", "ZAAK-3"]

        url = reverse("destruction:record-manager-create")
        data = {
            "name": "test list",
            "zaken": ",".join(zaken),
            "reviewers": [],
            "zaken_identificaties": ",".join(zaken_identificaties),
        }

        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertInHTML(
            '<li>reviewers<ul class="errorlist"><li>This field is required.</li></ul></li>',
            response.content.decode("utf-8"),
        )

    def test_reviewers_order_is_not_changed(self):
        # TODO: https://stackoverflow.com/questions/10296333/django-multiplechoicefield-does-not-preserve-order-of-selected-values
        reviewer = UserFactory.create_batch(3, role__can_review_destruction=True)
        zaken = [f"http://some.zaken.nl/api/v1/zaken/{i}" for i in range(1, 3)]
        zaken_identificaties = ["ZAAK-1", "ZAAK-2", "ZAAK-3"]

        url = reverse("destruction:record-manager-create")
        data = {
            "name": "test list",
            "zaken": ",".join(zaken),
            "reviewers": [reviewer[2].id, reviewer[1].id, reviewer[0].id],
            "zaken_identificaties": ",".join(zaken_identificaties),
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        destruction_list = DestructionList.objects.get()
        order_reviewers = destruction_list.assignees.order_by("order").values_list("assignee__id", flat=True)


        self.assertListEqual([reviewer[2].id, reviewer[1].id, reviewer[0].id], list(order_reviewers))
