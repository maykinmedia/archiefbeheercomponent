import logging
import traceback
from base64 import b64encode
from datetime import timedelta

from django.conf import settings
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from celery import chain
from timeline_logger.models import TimelineLog
from zds_client.client import ClientError
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from archiefbeheercomponent.notifications.models import Notification

from ..celery import app
from ..constants import RoleTypeChoices
from ..emails.constants import EmailTypeChoices
from ..emails.models import AutomaticEmail
from ..report.models import DestructionReport
from ..report.utils import create_destruction_report, get_absolute_url
from .constants import ListItemStatus, ListStatus, ReviewStatus
from .models import (
    ArchiveConfig,
    DestructionList,
    DestructionListAssignee,
    DestructionListItem,
    DestructionListReview,
)
from .service import fetch_resultaat, fetch_zaak, remove_zaak, update_zaak
from .utils import ServiceNotConfiguredError

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
    task_chain = chain(chunk_tasks.group(), notify_task)

    config = ArchiveConfig.get_solo()
    if config.create_zaak:
        create_zaak_task = create_destruction_zaak.si(list_id)
        task_chain = chain(task_chain, create_zaak_task)

    task_chain()


@app.task
def check_if_reviewers_need_reminder():
    archive_config = ArchiveConfig.get_solo()
    number_days = archive_config.days_until_reminder

    email = AutomaticEmail.objects.filter(type=EmailTypeChoices.review_reminder).first()

    if not email:
        return

    assignees = DestructionListAssignee.objects.filter(
        assignee=F("destruction_list__assignee"),
        assigned_on__lt=timezone.now() - timedelta(days=number_days),
        assignee__role__can_review_destruction=True,
        reminder_sent=False,
    ).select_related("assignee")

    for assignee in assignees:
        email.send(
            recipient=assignee.assignee, destruction_list=assignee.destruction_list
        )
        assignee.reminder_sent = True

    DestructionListAssignee.objects.bulk_update(assignees, ["reminder_sent"])


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
            template="destruction/logs/item_destruction_failed.html",
            extra_data={"zaak": None, "error": traceback.format_exc(),},
        )
        return

    try:
        resultaat = fetch_resultaat(zaak["resultaat"])
    except ClientError:
        resultaat = None

    try:
        if settings.ABC_DEMO_MODE:
            logger.warning(
                "[DEMO MODE] Zaak %r and related resources will not be deleted.",
                zaak.get("identificatie"),
            )
        else:
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
            template="destruction/logs/item_destruction_failed.html",
            extra_data={
                "zaak": zaak["identificatie"],
                "error": traceback.format_exc(),
            },
        )
    else:
        list_item.complete()
        TimelineLog.objects.create(
            content_object=list_item,
            template="destruction/logs/item_destruction_succeeded.html",
            extra_data={"zaak": zaak["identificatie"]},
        )

        list_item.extra_zaak_data = {
            "identificatie": zaak["identificatie"],
            "omschrijving": zaak.get("omschrijving") or "",
            "toelichting": zaak.get("toelichting") or "",
            "startdatum": zaak["startdatum"],
            "einddatum": zaak.get("einddatum") or "",
            "zaaktype": zaak["zaaktype"],
            "verantwoordelijke_organisatie": zaak["verantwoordelijkeOrganisatie"],
            "resultaat": resultaat,
            "relevante_andere_zaken": zaak.get("relevanteAndereZaken", []),
        }
        list_item.save()

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

    # Create the destruction report
    report = create_destruction_report(destruction_list)

    if report.process_owner:
        Notification.objects.create(
            destruction_list=destruction_list,
            user=report.process_owner,
            message=_(
                "Destruction list %(list)s has been processed. "
                "You can download the report of destruction here: %(url)s"
            )
            % {
                "list": destruction_list.name,
                "url": get_absolute_url(
                    reverse("report:download-report", args=[report.pk])
                ),
            },
        )

    # Send email to archivist role
    if destruction_list.items.filter(status=ListItemStatus.destroyed).exists():
        # Retrieve the assigned archivaris email
        approval_review = DestructionListReview.objects.filter(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author__role__type=RoleTypeChoices.archivist,
        ).last()

        if approval_review:
            assigned_archivaris = approval_review.author
            email = AutomaticEmail.objects.filter(
                type=EmailTypeChoices.report_available
            ).first()

            if email:
                email.send(
                    recipient=assigned_archivaris,
                    destruction_list=destruction_list,
                    report=report,
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
            template="destruction/logs/item_update_failed.html",
            extra_data={"zaak": None, "error": traceback.format_exc()},
        )
    else:
        TimelineLog.objects.create(
            content_object=list_item,
            template="destruction/logs/item_update_succeeded.html",
            extra_data={"zaak": zaak["identificatie"]},
        )


@app.task
def create_destruction_zaak(list_id):
    destruction_list = DestructionList.objects.get(id=list_id)
    destruction_report = DestructionReport.objects.get(
        destruction_list=destruction_list
    )
    config = ArchiveConfig.get_solo()

    zrc_service = Service.objects.filter(api_type=APITypes.zrc).first()
    if not zrc_service:
        raise ServiceNotConfiguredError("No service defined for the Zaken API")

    drc_service = Service.objects.filter(api_type=APITypes.drc).first()
    if not zrc_service:
        raise ServiceNotConfiguredError("No service defined for the Documenten API")

    zrc_client = zrc_service.build_client()
    drc_client = drc_service.build_client()
    today = timezone.now().date().isoformat()

    destruction_zaak = zrc_client.create(
        resource="zaak",
        data={
            "bronorganisatie": config.source_organisation,
            "omschrijving": _("Destruction List: %(list_name)s")
            % {"list_name": destruction_list.name},
            "zaaktype": config.case_type,
            "vertrouwelijkheidaanduiding": "openbaar",
            "startdatum": today,
            "verantwoordelijkeOrganisatie": config.source_organisation,
            "archiefnominatie": "blijvend_bewaren",
        },
    )
    logger.info(
        "Created zaak %s for destruction list %r",
        destruction_zaak["url"],
        destruction_list.id,
    )
    with destruction_report.content_pdf.open("rb") as f:
        destruction_document = drc_client.create(
            resource="enkelvoudiginformatieobject",
            data={
                "bronorganisatie": config.source_organisation,
                "creatiedatum": today,
                "titel": _("Destruction Report: %(list_name)s")
                % {"list_name": destruction_list.name},
                "auteur": "Archiefbeheercomponent",
                "taal": "nld",
                "formaat": "pdf",
                "inhoud": b64encode(f.read()).decode("utf-8"),
                "informatieobjecttype": config.document_type,
                "indicatie_gebruiksrecht": False,
            },
        )
    logger.info(
        "Created document %s from destruction report of destruction list %r",
        destruction_document["url"],
        destruction_list.id,
    )

    zrc_client.create(
        resource="zaakinformatieobject",
        data={
            "zaak": destruction_zaak["url"],
            "informatieobject": destruction_document["url"],
        },
    )
    zrc_client.create(
        resource="resultaat",
        data={"zaak": destruction_zaak["url"], "resultaattype": config.result_type},
    )
    zrc_client.create(
        resource="status",
        data={
            "zaak": destruction_zaak["url"],
            "statustype": config.status_type,
            "datum_status_gezet": timezone.now().isoformat(),
        },
    )

    destruction_list.zaak_url = destruction_zaak["url"]
    destruction_list.save()