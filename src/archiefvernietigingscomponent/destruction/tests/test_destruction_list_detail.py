from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from django_capture_on_commit_callbacks import capture_on_commit_callbacks
from django_webtest import WebTest
from timeline_logger.models import TimelineLog

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory
from archiefvernietigingscomponent.notifications.models import Notification

from ...constants import RoleTypeChoices
from ..constants import ListItemStatus, ListStatus, ReviewStatus, Suggestion
from ..models import DestructionList, DestructionListItem, DestructionListReviewComment
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


@patch("archiefvernietigingscomponent.destruction.views.update_zaken.delay")
class DestructionListUpdateTests(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.user = UserFactory(role__can_start_destruction=True)
        self.client.force_login(self.user)

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
        self.assertEqual(notification.message, _("You are assigned for review."))

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

    def test_abort_destruction_list(self, m):
        destruction_list = DestructionListFactory.create(
            author=self.user, assignee=self.user
        )
        list_items = DestructionListItemFactory.create_batch(
            3, destruction_list=destruction_list
        )
        url = reverse("destruction:record-manager-detail", args=[destruction_list.id])
        data = {"abort": "abort"}
        data.update(MANAGEMENT_FORM_DATA)
        for i, list_item in enumerate(list_items):
            data.update(
                {
                    f"items-{i}-id": list_item.id,
                    f"items-{i}-action": "",
                    f"items-{i}-archiefnominatie": "blijvend_bewaren",
                    f"items-{i}-archiefactiedatum": "2020-06-17",
                }
            )

        # with capture_on_commit_callbacks(execute=True) as callbacks:
        response = self.client.post(url, data=data)

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        # can't refresh_from_db because of fsm protection
        destruction_list = DestructionList.objects.get(id=destruction_list.id)
        self.assertEqual(destruction_list.assignee, None)
        self.assertEqual(destruction_list.status, ListStatus.completed)

        # check items statuses
        for item in list_items:
            list_item = DestructionListItem.objects.get(id=item.id)
            self.assertEqual(list_item.status, ListItemStatus.removed)

        # check log
        timeline_log = TimelineLog.objects.get()
        self.assertEqual(timeline_log.user, self.user)
        self.assertEqual(timeline_log.template, "destruction/logs/aborted.txt")

        # Check notification
        # Since the User is both the author and the assignee, no notification is sent
        notifications = Notification.objects.filter(destruction_list=destruction_list)

        self.assertEqual(0, notifications.count())

        # check no zaken update
        m.assert_not_called()

    def test_abort_destruction_list_notify_assignee(self, m):
        """
        Test that if the author of the DL and the assignee are NOT the same, when the DL is aborted a notification is
        sent to the assignee.
        """
        assignee = UserFactory.create(role__can_review_destruction=True)
        destruction_list = DestructionListFactory.create(
            author=self.user, assignee=assignee
        )
        list_items = DestructionListItemFactory.create_batch(
            3, destruction_list=destruction_list
        )
        url = reverse("destruction:record-manager-detail", args=[destruction_list.id])
        data = {"abort": "abort"}
        data.update(MANAGEMENT_FORM_DATA)
        for i, list_item in enumerate(list_items):
            data.update(
                {
                    f"items-{i}-id": list_item.id,
                    f"items-{i}-action": "",
                    f"items-{i}-archiefnominatie": "blijvend_bewaren",
                    f"items-{i}-archiefactiedatum": "2020-06-17",
                }
            )

        # with capture_on_commit_callbacks(execute=True) as callbacks:
        response = self.client.post(url, data=data)

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        # can't refresh_from_db because of fsm protection
        destruction_list = DestructionList.objects.get(id=destruction_list.id)
        self.assertEqual(destruction_list.assignee, None)
        self.assertEqual(destruction_list.status, ListStatus.completed)

        # check items statuses
        for item in list_items:
            list_item = DestructionListItem.objects.get(id=item.id)
            self.assertEqual(list_item.status, ListItemStatus.removed)

        # check log
        timeline_log = TimelineLog.objects.get()
        self.assertEqual(timeline_log.user, self.user)
        self.assertEqual(timeline_log.template, "destruction/logs/aborted.txt")

        # Check notification
        notifications = Notification.objects.filter(destruction_list=destruction_list)

        self.assertEqual(1, notifications.count())

        notification = notifications.get()

        self.assertEqual(
            _(
                "%(author)s has aborted the destruction list. No further action is required."
            )
            % {"author": destruction_list.author},
            notification.message,
        )

        # check no zaken update
        m.assert_not_called()

    def test_cant_abort_completed_destruction_list(self, m):
        destruction_list = DestructionListFactory.create(
            author=self.user, assignee=self.user, status=ListStatus.completed
        )
        list_items = DestructionListItemFactory.create_batch(
            3, destruction_list=destruction_list
        )

        url = reverse("destruction:record-manager-detail", args=[destruction_list.id])
        data = {"abort": "abort"}
        data.update(MANAGEMENT_FORM_DATA)
        for i, list_item in enumerate(list_items):
            data.update(
                {
                    f"items-{i}-id": list_item.id,
                    f"items-{i}-action": "",
                    f"items-{i}-archiefnominatie": "blijvend_bewaren",
                    f"items-{i}-archiefactiedatum": "2020-06-17",
                }
            )

        response = self.client.post(url, data=data)

        self.assertEqual(400, response.status_code)
        self.assertEqual(
            _(
                "The destruction of this list can't be aborted because it has already been completed."
            ),
            response.content.decode("utf-8"),
        )

    def test_list_author_can_comment_on_review(self, m):
        record_manager = UserFactory(
            role__can_start_destruction=True, role__type=RoleTypeChoices.archivist
        )
        process_owner = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.process_owner
        )

        destruction_list = DestructionListFactory.create(author=record_manager)

        item = DestructionListItemFactory.create(destruction_list=destruction_list)
        DestructionListAssigneeFactory.create(
            assignee=record_manager, destruction_list=destruction_list
        )
        destruction_list.assignee = record_manager
        destruction_list.save()

        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            author=process_owner,
            status=ReviewStatus.changes_requested,
        )

        data = {
            "items-TOTAL_FORMS": 1,
            "items-INITIAL_FORMS": 1,
            "items-MIN_NUM_FORMS": 0,
            "items-MAX_NUM_FORMS": 1000,
            "text": "I disagree with these comments!",
            "items-0-id": item.id,
            "items-0-action": "",
            "items-0-archiefnominatie": "blijvend_bewaren",
            "items-0-archiefactiedatum": "2020-06-17",
        }

        self.client.force_login(record_manager)
        response = self.client.post(
            reverse("destruction:record-manager-detail", args=[destruction_list.pk]),
            data=data,
        )

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        comments = DestructionListReviewComment.objects.all()

        self.assertEqual(1, comments.count())

        comment = comments.get()

        self.assertEqual("I disagree with these comments!", comment.text)
        self.assertEqual(record_manager, comment.review.destruction_list.author)
        self.assertEqual(destruction_list.last_review(), comment.review)

    def test_list_author_can_leave_comment_empty(self, m):
        record_manager = UserFactory(
            role__can_start_destruction=True, role__type=RoleTypeChoices.archivist
        )
        process_owner = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.process_owner
        )

        destruction_list = DestructionListFactory.create(author=record_manager)

        item = DestructionListItemFactory.create(destruction_list=destruction_list)
        DestructionListAssigneeFactory.create(
            assignee=record_manager, destruction_list=destruction_list
        )
        destruction_list.assignee = record_manager
        destruction_list.save()

        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            author=process_owner,
            status=ReviewStatus.changes_requested,
        )

        data = {
            "items-TOTAL_FORMS": 1,
            "items-INITIAL_FORMS": 1,
            "items-MIN_NUM_FORMS": 0,
            "items-MAX_NUM_FORMS": 1000,
            "items-0-id": item.id,
            "items-0-action": "",
            "items-0-archiefnominatie": "blijvend_bewaren",
            "items-0-archiefactiedatum": "2020-06-17",
        }

        self.client.force_login(record_manager)
        response = self.client.post(
            reverse("destruction:record-manager-detail", args=[destruction_list.pk]),
            data=data,
        )

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        comments = DestructionListReviewComment.objects.all()

        self.assertEqual(0, comments.count())

    def test_empty_comment_is_not_saved(self, m):
        record_manager = UserFactory(
            role__can_start_destruction=True, role__type=RoleTypeChoices.archivist
        )
        process_owner = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.process_owner
        )

        destruction_list = DestructionListFactory.create(author=record_manager)

        item = DestructionListItemFactory.create(destruction_list=destruction_list)
        DestructionListAssigneeFactory.create(
            assignee=record_manager, destruction_list=destruction_list
        )
        destruction_list.assignee = record_manager
        destruction_list.save()

        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            author=process_owner,
            status=ReviewStatus.changes_requested,
        )

        data = {
            "items-TOTAL_FORMS": 1,
            "items-INITIAL_FORMS": 1,
            "items-MIN_NUM_FORMS": 0,
            "items-MAX_NUM_FORMS": 1000,
            "items-0-id": item.id,
            "items-0-action": "",
            "items-0-archiefnominatie": "blijvend_bewaren",
            "items-0-archiefactiedatum": "2020-06-17",
            "text": "",
        }

        self.client.force_login(record_manager)
        response = self.client.post(
            reverse("destruction:record-manager-detail", args=[destruction_list.pk]),
            data=data,
        )

        self.assertRedirects(response, reverse("destruction:record-manager-list"))

        comments = DestructionListReviewComment.objects.all()

        self.assertEqual(0, comments.count())

    def test_list_author_cannot_comment_on_approved_list(self, m):
        record_manager = UserFactory(
            role__can_start_destruction=True, role__type=RoleTypeChoices.archivist
        )
        process_owner = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.process_owner
        )

        destruction_list = DestructionListFactory.create(author=record_manager)

        DestructionListItemFactory.create_batch(2, destruction_list=destruction_list)

        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            author=process_owner,
            status=ReviewStatus.approved,
        )

        self.client.force_login(record_manager)
        response = self.client.get(
            reverse("destruction:record-manager-detail", args=[destruction_list.pk]),
            user=record_manager,
        )

        self.assertEqual(200, response.status_code)

        self.assertNotIn(b"<textarea", response.content)


class DestructionListDetailTests(WebTest):
    """
    check that the user can update DL if they are the author and the current assignee of DL
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory(role__can_start_destruction=True)

    def setUp(self) -> None:
        super().setUp()

        self.app.set_user(self.user)

    def test_can_update_and_abort(self):
        destruction_list = DestructionListFactory.create(
            author=self.user, assignee=self.user
        )
        url = reverse("destruction:record-manager-detail", args=[destruction_list.id])

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)

        submit_btn = response.html.find("button", type="submit", value="submit")
        self.assertIsNotNone(submit_btn)
        abort_btn = response.html.find("button", type="submit", value="abort")
        self.assertIsNotNone(abort_btn)

    def test_author_cannot_update_but_can_abort(self):
        destruction_list = DestructionListFactory.create(author=self.user)
        url = reverse("destruction:record-manager-detail", args=[destruction_list.id])

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)

        submit_btn = response.html.find("button", type="submit", value="submit")
        self.assertIsNone(submit_btn)
        abort_btn = response.html.find("button", type="submit", value="abort")
        self.assertIsNotNone(abort_btn)

    def test_assignee_cannot_update_and_cannot_abort(self):
        destruction_list = DestructionListFactory.create()
        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=self.user
        )
        url = reverse("destruction:record-manager-detail", args=[destruction_list.id])

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)

        submit_btn = response.html.find("button", type="submit", value="submit")
        self.assertIsNone(submit_btn)
        abort_btn = response.html.find("button", type="submit", value="abort")
        self.assertIsNone(abort_btn)

    def test_cannot_update_or_abort_completed_list(self):
        destruction_list = DestructionListFactory.create(
            author=self.user, assignee=self.user, status=ListStatus.completed
        )
        url = reverse("destruction:record-manager-detail", args=[destruction_list.id])

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)

        submit_btn = response.html.find("button", type="submit", value="submit")
        self.assertIsNone(submit_btn)
        abort_btn = response.html.find("button", type="submit", value="abort")
        self.assertIsNone(abort_btn)
