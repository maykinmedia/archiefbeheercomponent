from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from rma.accounts.tests.factories import UserFactory
from rma.notifications.models import Notification

from ..constants import ReviewStatus, Suggestion
from ..models import DestructionListReview
from .factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
    DestructionListItemFactory,
)

MANAGEMENT_FORM_DATA = {
    "item_reviews-TOTAL_FORMS": 3,
    "item_reviews-INITIAL_FORMS": 0,
    "item_reviews-MIN_NUM_FORMS": 0,
    "item_reviews-MAX_NUM_FORMS": 1000,
}


class ReviewCreateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory(role__can_review_destruction=True)

    def setUp(self) -> None:
        super().setUp()

        self.client.force_login(self.user)

    def _create_destruction_list(self):
        destruction_list = DestructionListFactory.create()

        DestructionListItemFactory.create_batch(3, destruction_list=destruction_list)
        assignee = DestructionListAssigneeFactory.create(
            assignee=self.user, destruction_list=destruction_list
        )
        destruction_list.assignee = assignee.assignee
        destruction_list.save()

        return destruction_list

    def test_create_review_approve(self):
        destruction_list = self._create_destruction_list()
        next_assignee = DestructionListAssigneeFactory.create(
            destruction_list=destruction_list
        )

        url = reverse("destruction:reviewer-create", args=[destruction_list.id])

        data = {
            "author": self.user.id,
            "destruction_list": destruction_list.id,
            "status": ReviewStatus.approved,
            "text": "some comment",
        }
        data.update(MANAGEMENT_FORM_DATA)
        for i, item in enumerate(destruction_list.items.all()):
            data.update(
                {
                    f"item_reviews-{i}-destruction_list_item": item.id,
                    f"item_reviews-{i}-suggestion": "",
                    f"item_reviews-{i}-text": "",
                }
            )

        response = self.client.post(url, data=data)

        self.assertRedirects(response, reverse("destruction:reviewer-list"))

        review = DestructionListReview.objects.get()

        self.assertEqual(review.author, self.user)
        self.assertEqual(review.destruction_list, destruction_list)
        self.assertEqual(review.status, ReviewStatus.approved)
        self.assertEqual(review.text, "some comment")

        items_reviews = review.item_reviews.all()
        self.assertEqual(items_reviews.count(), 0)  # save only changed items

        self.assertEqual(review.destruction_list.assignee, next_assignee.assignee)

        #  check logs
        timeline_log = review.logs.get()
        self.assertEqual(timeline_log.user, self.user)
        self.assertEqual(timeline_log.template, "destruction/logs/review_created.txt")

        #  check notifications
        notifications = Notification.objects.all()
        self.assertEqual(notifications.count(), 2)
        notif_review = notifications.get(user=destruction_list.author)
        self.assertEqual(
            notif_review.message, f"Destruction list has been reviewed by {self.user}"
        )
        notif_assign = notifications.get(user=next_assignee.assignee)
        self.assertEqual(
            notif_assign.message, "You are assigned to the destruction list"
        )

    def test_create_review_change(self):
        destruction_list = self._create_destruction_list()
        next_assignee = DestructionListAssigneeFactory.create(
            destruction_list=destruction_list
        )
        items = destruction_list.items.order_by("id").all()

        url = reverse("destruction:reviewer-create", args=[destruction_list.id])

        data = {
            "author": self.user.id,
            "destruction_list": destruction_list.id,
            "status": ReviewStatus.changes_requested,
            "item_reviews-0-destruction_list_item": items[0].id,
            "item_reviews-0-suggestion": Suggestion.change_and_remove,
            "item_reviews-0-text": "some comment",
            "item_reviews-1-destruction_list_item": items[1].id,
            "item_reviews-1-suggestion": Suggestion.remove,
            "item_reviews-1-text": "",
            "item_reviews-2-destruction_list_item": items[2].id,
            "item_reviews-2-suggestion": "",
            "item_reviews-2-text": "",
        }
        data.update(MANAGEMENT_FORM_DATA)

        response = self.client.post(url, data=data)

        self.assertRedirects(response, reverse("destruction:reviewer-list"))

        review = DestructionListReview.objects.get()

        self.assertEqual(review.author, self.user)
        self.assertEqual(review.destruction_list, destruction_list)
        self.assertEqual(review.status, ReviewStatus.changes_requested)

        item_reviews = review.item_reviews.order_by("destruction_list_item_id").all()
        self.assertEqual(item_reviews.count(), 2)  # save only changed items
        self.assertEqual(item_reviews[0].destruction_list_item, items[0])
        self.assertEqual(item_reviews[0].suggestion, Suggestion.change_and_remove)
        self.assertEqual(item_reviews[1].destruction_list_item, items[1])
        self.assertEqual(item_reviews[1].suggestion, Suggestion.remove)

        self.assertEqual(review.destruction_list.assignee, destruction_list.author)

        #  check logs
        timeline_log = review.logs.get()
        self.assertEqual(timeline_log.user, self.user)
        self.assertEqual(timeline_log.template, "destruction/logs/review_created.txt")

        #  check notifications
        notifications = Notification.objects.order_by("message").all()
        self.assertEqual(notifications.count(), 2)
        self.assertEqual(notifications[0].user, destruction_list.author)
        self.assertEqual(
            notifications[0].message,
            f"Destruction list has been reviewed by {self.user}",
        )
        self.assertEqual(notifications[1].user, destruction_list.author)
        self.assertEqual(
            notifications[1].message, "You are assigned to the destruction list"
        )

    @patch("rma.destruction.views.process_destruction_list.delay")
    def test_create_review_approve_last(self, m):
        destruction_list = self._create_destruction_list()

        url = reverse("destruction:reviewer-create", args=[destruction_list.id])

        data = {
            "author": self.user.id,
            "destruction_list": destruction_list.id,
            "status": ReviewStatus.approved,
            "text": "some comment",
        }
        data.update(MANAGEMENT_FORM_DATA)

        response = self.client.post(url, data=data)

        self.assertRedirects(response, reverse("destruction:reviewer-list"))

        review = DestructionListReview.objects.get()

        self.assertEqual(review.author, self.user)
        self.assertEqual(review.destruction_list, destruction_list)
        self.assertEqual(review.status, ReviewStatus.approved)
        self.assertEqual(review.text, "some comment")

        #  check logs
        timeline_log = review.logs.get()
        self.assertEqual(timeline_log.user, self.user)
        self.assertEqual(timeline_log.template, "destruction/logs/review_created.txt")

        #  check notification
        notification = Notification.objects.get()
        self.assertEqual(notification.user, destruction_list.author)
        self.assertEqual(
            notification.message, f"Destruction list has been reviewed by {self.user}"
        )

        #  check task call
        m.assert_called_once_with(destruction_list.id)
