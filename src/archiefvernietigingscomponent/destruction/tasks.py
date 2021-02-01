import logging
import traceback

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from celery import chain
from timeline_logger.models import TimelineLog
from zds_client.client import ClientError

from archiefvernietigingscomponent.notifications.models import Notification

from ..celery import app
from .constants import ListItemStatus, ListStatus
from .models import DestructionList, DestructionListItem
from .service import fetch_zaak, remove_zaak, update_zaak

logger = logging.getLogger(__name__)


@app.task
def process_destruction_list(list_id):
    try:
        destruction_list = DestructionList.objects.get(id=list_id)
    except DestructionList.DoesNotExist:
        logger.warning("Destruction list %r can not be retrieved", list_id)
        return

    if destruction_list.status != ListStatus.in_progress:
        logger.warning("Destruction list %r has been already processed", list_id)
        return

    destruction_list.process()
    destruction_list.save()

    list_item_ids = [
        (list_item.id,)
        for list_item in destruction_list.items.filter(status=ListItemStatus.suggested)
        .order_by("id")
        .all()
    ]
    chunk_tasks = process_list_item.chunks(list_item_ids, settings.ZAKEN_PER_TASK)
    notify_task = complete_and_notify.si(list_id)
    chain(chunk_tasks.group(), notify_task)()


@app.task
def process_list_item(list_item_id):
    list_item = DestructionListItem.objects.get(id=list_item_id)
    list_item.process()
    list_item.save()

    try:
        zaak = fetch_zaak(list_item.zaak)
    except ClientError as exc:
        logger.warning(
            "Destruction list item %r has failed during execution with error: %r",
            list_item.id,
            exc,
            exc_info=True,
        )

        list_item.fail()
        list_item.save()
        TimelineLog.objects.create(
            content_object=list_item,
            template="destruction/logs/item_destruction_failed.txt",
            extra_data={"zaak": None, "error": traceback.format_exc(),},
        )
        return

    try:
        remove_zaak(list_item.zaak)
    except ClientError as exc:
        logger.warning(
            "Destruction list item %r has failed during execution with error: %r",
            list_item.id,
            exc,
            exc_info=True,
        )

        list_item.fail()
        TimelineLog.objects.create(
            content_object=list_item,
            template="destruction/logs/item_destruction_failed.txt",
            extra_data={
                "zaak": zaak["identificatie"],
                "error": traceback.format_exc(),
            },
        )
    else:
        list_item.complete()
        TimelineLog.objects.create(
            content_object=list_item,
            template="destruction/logs/item_destruction_succeeded.txt",
            extra_data={"zaak": zaak["identificatie"]},
        )

    list_item.save()
    return list_item.status


@app.task
def complete_and_notify(list_id):
    destruction_list = DestructionList.objects.get(id=list_id)

    destruction_list.complete()
    destruction_list.save()

    logger.info("Destruction list %r is processed", destruction_list.id)

    notification = Notification.objects.create(
        destruction_list=destruction_list,
        user=destruction_list.author,
        message=_("Processing of the list is complete."),
    )
    return notification.id


@app.task
def update_zaken(update_data: list):
    if not update_data:
        return

    chunk_tasks = update_zaak_from_list_item.chunks(
        update_data, settings.ZAKEN_PER_TASK
    )
    chunk_tasks.group()()


@app.task
def update_zaak_from_list_item(list_item_id: str, archive_data: dict):

    try:
        list_item = DestructionListItem.objects.get(id=list_item_id)
    except DestructionListItem.DoesNotExist:
        logger.warning("Destruction list item %r can not be retrieved", list_item_id)
        return

    if list_item.status != ListItemStatus.removed:
        logger.warning(
            "Destruction list item %r has been already processed", list_item_id
        )
        return

    review = list_item.item_reviews.order_by("id").first()
    audit_comment = review.text if review else None

    try:
        zaak = update_zaak(list_item.zaak, archive_data, audit_comment)
    except ClientError as exc:
        logger.warning(
            "Destruction list item %r has failed during execution with error: %r",
            list_item.id,
            exc,
            exc_info=True,
        )

        TimelineLog.objects.create(
            content_object=list_item,
            template="destruction/logs/item_update_failed.txt",
            extra_data={"zaak": None, "error": traceback.format_exc()},
        )
    else:
        TimelineLog.objects.create(
            content_object=list_item,
            template="destruction/logs/item_update_succeeded.txt",
            extra_data={"zaak": zaak["identificatie"]},
        )
