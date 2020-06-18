import logging

from .constants import ListStatus
from .models import DestructionList

logger = logging.getLogger(__name__)


def process_destruction_list(list_id):
    try:
        destruction_list = DestructionList.objects.get(id=list_id)
    except DestructionList.DoesNotExist:
        logger.warning("Destructin list %r can not be retrieved", list_id)
        return

    if not destruction_list.status != ListStatus.in_progress:
        logger.warning("Destructin list %r has been already processed", list_id)
        return

    destruction_list.process()
    destruction_list.save(update_fields=["status"])

    # TODO async or another task?
    for list_item in destruction_list.items.all():
        list_item.process()
        list_item.save(update_fields=["status"])
        list_item.complete()
        list_item.save(update_fields=["status"])

    destruction_list.complete()
    destruction_list.save(update_fields=["status"])

    # TODO send make notification
