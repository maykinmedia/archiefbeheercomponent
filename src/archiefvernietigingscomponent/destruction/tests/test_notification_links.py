"""
Tests for the notification links.
"""
from django.test import tag
from django.urls import reverse, reverse_lazy

from django_webtest import WebTest

from archiefvernietigingscomponent.accounts.tests.factories import (
    RoleFactory,
    UserFactory,
)

from .factories import DestructionListAssigneeFactory, DestructionListFactory


@tag("notifs")
class NotificationLinkTests(WebTest):

    start_url = reverse_lazy("entry")

    @classmethod
    def setUpTestData(cls):
        record_manager = RoleFactory.create(record_manager=True)
        process_owner = RoleFactory.create(process_owner=True)
        archivaris = RoleFactory.create(archivaris=True)

        user1 = UserFactory.create(role=record_manager)
        user2 = UserFactory.create(role=process_owner)
        user3 = UserFactory.create(role=archivaris)

        destruction_list = DestructionListFactory.create(author=user1)
        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=user2
        )
        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=user3
        )

        cls.destruction_list = destruction_list
        cls.user1 = user1
        cls.user2 = user2
        cls.user3 = user3

    def test_first_reviewer(self):
        # assigning creates the notification
        self.destruction_list.assign(self.user2)
        self.destruction_list.save()
        self.app.set_user(self.user2)
        # from landing page, 'click' the link of the notification
        response = self.app.get(self.start_url, auto_follow=True)
        link = response.pyquery(
            ".notifications-list .notifications-list__notif-goto:first"
        )

        new_page = response.click(href=link.attr("href")).follow()

        self.assertEqual(new_page.status_code, 200)
        self.assertEqual(
            new_page.request.path,
            reverse(
                "destruction:reviewer-create",
                kwargs={"destruction_list": self.destruction_list.id},
            ),
        )

    def test_second_reviewer(self):
        # assigning creates the notification
        self.destruction_list.assign(self.user3)
        self.destruction_list.save()
        # from landing page, 'click' the link of the notification
        self.app.set_user(self.user3)
        response = self.app.get(self.start_url, auto_follow=True)
        link = response.pyquery(
            ".notifications-list .notifications-list__notif-goto:first"
        )

        new_page = response.click(href=link.attr("href")).follow()

        self.assertEqual(new_page.status_code, 200)
        self.assertEqual(
            new_page.request.path,
            reverse(
                "destruction:reviewer-create",
                kwargs={"destruction_list": self.destruction_list.id},
            ),
        )

    def test_author(self):
        # assigning creates the notification
        self.destruction_list.assign(self.user1)
        self.destruction_list.save()
        # from landing page, 'click' the link of the notification
        self.app.set_user(self.user1)
        response = self.app.get(self.start_url, auto_follow=True)
        link = response.pyquery(
            ".notifications-list .notifications-list__notif-goto:first"
        )

        new_page = response.click(href=link.attr("href")).follow()

        self.assertEqual(new_page.status_code, 200)
        self.assertEqual(
            new_page.request.path,
            reverse(
                "destruction:record-manager-detail",
                kwargs={"pk": self.destruction_list.id},
            ),
        )

    def test_reviewer_but_not_current(self):
        # assigning creates the notification
        self.destruction_list.assign(self.user2)
        self.destruction_list.save()
        self.destruction_list.assign(self.user3)
        self.destruction_list.save()
        # from landing page, 'click' the link of the notification
        self.app.set_user(self.user2)
        response = self.app.get(self.start_url, auto_follow=True)
        link = response.pyquery(
            ".notifications-list .notifications-list__notif-goto:first"
        )

        self.app.get(link.attr("href"), status=403)
