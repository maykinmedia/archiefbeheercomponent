from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.utils.translation import gettext as _

import requests_mock
from timeline_logger.models import TimelineLog
from zds_client.client import ClientError
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from archiefvernietigingscomponent.notifications.models import Notification

from ...accounts.tests.factories import UserFactory
from ...tests.utils import generate_oas_component, mock_service_oas_get
from ..constants import ListItemStatus, ListStatus, ReviewStatus
from ..models import DestructionList, DestructionListItem
from ..tasks import (
    complete_and_notify,
    process_destruction_list,
    process_list_item,
    update_zaak_from_list_item,
    update_zaken,
)
from ..utils import (
    create_destruction_report,
    get_destruction_list_archivaris_comments,
    get_process_owner_comments,
    get_vernietigings_categorie_selectielijst,
)
from .factories import (
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


@requests_mock.Mocker()
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

    @override_settings(DEFAULT_FROM_EMAIL="email@test.avc")
    def test_all_deleted_cases_are_in_destruction_report(self, m):
        archivaris = UserFactory.create(
            role__can_review_destruction=True, role__can_view_case_details=False,
        )

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

        self.assertEqual("email@test.avc", sent_mail.from_email)
        self.assertIn(archivaris.email, sent_mail.to)
        self.assertIn("<td>ZAAK-1</td>", sent_mail.body)
        self.assertIn("<td>ZAAK-2</td>", sent_mail.body)

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
            },
        )

        complete_and_notify(destruction_list.id)

        self.assertEqual(0, len(mail.outbox))


@requests_mock.Mocker()
class DestructionReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        Service.objects.create(
            label="Selectielijst API",
            api_type=APITypes.orc,
            api_root="https://selectielijst.oz.nl/api/v1",
            oas="https://selectielijst.oz.nl/api/v1/schema/openapi.json",
        )
        Service.objects.create(
            label="Catalogi API",
            api_type=APITypes.ztc,
            api_root="https://oz.nl/catalogi/api/v1",
            oas="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )

    def test_destruction_report_generation(self, m):
        destruction_list = DestructionListFactory.create(name="Winter cases")
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
            },
        )

        mock_service_oas_get(
            m,
            "https://selectielijst.oz.nl/api/v1",
            "orc",
            oas_url="https://selectielijst.oz.nl/api/v1/schema/openapi.json",
        )
        mock_service_oas_get(
            m,
            "https://oz.nl/catalogi/api/v1",
            "ztc",
            oas_url="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
            json={
                "selectielijstProcestype": "https://selectielijst.oz.nl/api/v1/procestypen/uuid-1"
            },
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
            json={
                "selectielijstProcestype": "https://selectielijst.oz.nl/api/v1/procestypen/uuid-2"
            },
        )
        m.get(
            url="https://selectielijst.oz.nl/api/v1/procestypen/uuid-1",
            json={"nummer": 1},
        )
        m.get(
            url="https://selectielijst.oz.nl/api/v1/procestypen/uuid-2",
            json={"nummer": 2},
        )

        report = create_destruction_report(destruction_list)

        self.assertIn("<td>ZAAK-1</td>", report)
        self.assertIn("<td>Een zaak</td>", report)
        self.assertIn("<td>366 days</td>", report)
        self.assertIn("<td>1</td>", report)
        self.assertIn("<td>Onderdeel van vernietigingslijst: Winter cases</td>", report)

        self.assertIn("<td>ZAAK-2</td>", report)
        self.assertIn("<td>Een andere zaak</td>", report)
        self.assertIn("<td>394 days</td>", report)
        self.assertIn("<td>2</td>", report)

    def test_failed_destruction_not_in_report(self, m):
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )

        mock_service_oas_get(
            m,
            "https://selectielijst.oz.nl/api/v1",
            "orc",
            oas_url="https://selectielijst.oz.nl/api/v1/schema/openapi.json",
        )
        mock_service_oas_get(
            m,
            "https://oz.nl/catalogi/api/v1",
            "ztc",
            oas_url="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
            json={
                "selectielijstProcestype": "https://selectielijst.oz.nl/api/v1/procestypen/uuid-2"
            },
        )
        m.get(
            url="https://selectielijst.oz.nl/api/v1/procestypen/uuid-2",
            json={"nummer": 2},
        )

        report = create_destruction_report(destruction_list)

        self.assertNotIn("<td>ZAAK-1</td>", report)
        self.assertNotIn("<td>Een zaak</td>", report)
        self.assertNotIn("<td>366 days</td>", report)
        self.assertNotIn("<td>1</td>", report)

        self.assertIn("<td>ZAAK-2</td>", report)
        self.assertIn("<td>Een andere zaak</td>", report)
        self.assertIn("<td>394 days</td>", report)
        self.assertIn("<td>2</td>", report)

    def test_no_selectielijst_client(self, m):
        mock_service_oas_get(
            m,
            "https://oz.nl/catalogi/api/v1",
            "ztc",
            oas_url="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
            json={
                "selectielijstProcestype": "https://another-selectielijst.oz.nl/api/v1/procestypen/uuid-1"
            },
        )

        number = get_vernietigings_categorie_selectielijst(
            "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1"
        )

        self.assertEqual("", number)

    def test_no_process_type_url(self, m):
        mock_service_oas_get(
            m,
            "https://oz.nl/catalogi/api/v1",
            "ztc",
            oas_url="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        m.get(url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1", json={})

        number = get_vernietigings_categorie_selectielijst(
            "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1"
        )

        self.assertEqual("", number)

    def test_comments_archivaris(self, m):
        archivaris = UserFactory.create(
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )

        comment = get_destruction_list_archivaris_comments(destruction_list)

        self.assertEqual("What a magnificent list!", comment)

    def test_only_comments_from_archivaris_returned(self, m):
        archivaris = UserFactory.create(
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        process_owner = UserFactory.create(
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="I am happy with this list!",
        )

        comment = get_destruction_list_archivaris_comments(destruction_list)

        self.assertEqual("What a magnificent list!", comment)

    def test_only_latest_comment_from_archivaris_is_returned(self, m):
        archivaris = UserFactory.create(
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="I am happy with this list!",
        )

        comment = get_destruction_list_archivaris_comments(destruction_list)

        self.assertEqual("I am happy with this list!", comment)

    def test_only_approval_comment_from_archivaris_is_returned(self, m):
        archivaris = UserFactory.create(
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.changes_requested,
            author=archivaris,
            text="Could you remove the first zaak?",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="I am happy with this list now!",
        )

        comment = get_destruction_list_archivaris_comments(destruction_list)

        self.assertEqual("I am happy with this list now!", comment)

    def test_comments_process_owner(self, m):
        process_owner = UserFactory.create(
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="What a magnificent list!",
        )

        comment = get_process_owner_comments(destruction_list)

        self.assertEqual("What a magnificent list!", comment)

    def test_only_comments_from_process_owner_returned(self, m):
        archivaris = UserFactory.create(
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        process_owner = UserFactory.create(
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="I am happy with this list!",
        )

        comment = get_process_owner_comments(destruction_list)

        self.assertEqual("I am happy with this list!", comment)

    def test_only_latest_comment_from_process_owner_is_returned(self, m):
        process_owner = UserFactory.create(
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="What a magnificent list!",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="I am happy with this list!",
        )

        comment = get_process_owner_comments(destruction_list)

        self.assertEqual("I am happy with this list!", comment)

    def test_only_approval_comment_from_process_owner_is_returned(self, m):
        process_owner = UserFactory.create(
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.changes_requested,
            author=process_owner,
            text="Could you remove the first zaak?",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="I am happy with this list now!",
        )

        comment = get_process_owner_comments(destruction_list)

        self.assertEqual("I am happy with this list now!", comment)


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
