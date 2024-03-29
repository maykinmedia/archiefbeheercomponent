from datetime import timedelta
from typing import Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_fsm import FSMField, transition
from ordered_model.models import OrderedModel
from privates.fields import PrivateMediaFileField
from solo.models import SingletonModel
from timeline_logger.models import TimelineLog

from archiefbeheercomponent.accounts.models import User
from archiefbeheercomponent.notifications.models import Notification

from ..emails.constants import EmailTypeChoices
from ..emails.models import AutomaticEmail
from .constants import (
    ListItemStatus,
    ListStateDisplay,
    ListStatus,
    ReviewStatus,
    Suggestion,
)


class DestructionList(models.Model):
    name = models.CharField(_("name"), max_length=200, unique=True)
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="created_lists",
        verbose_name=_("author"),
        help_text=_("Creator of destruction list."),
    )
    created = models.DateTimeField(_("created"), default=timezone.now)
    end = models.DateTimeField(_("end"), blank=True, null=True)
    assignee = models.ForeignKey(
        "accounts.User",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="assigned_lists",
        verbose_name=_("assignee"),
        help_text=_("Currently assigned user."),
    )
    status = FSMField(
        _("status"),
        default=ListStatus.in_progress,
        choices=ListStatus.choices,
        protected=True,
        max_length=80,
    )
    logs = GenericRelation(TimelineLog)
    contains_sensitive_info = models.BooleanField(
        verbose_name=_("contains sensitive information"),
        help_text=_(
            "Specify whether this destruction list contains privacy sensitive data. "
            "If set to true, the report of destruction will NOT contain case "
            "descriptions or the remarks by the archivist."
        ),
        default=True,
    )
    zaak_url = models.URLField(
        _("zaak URL"),
        help_text=_(
            "The URL of the case containing the destruction report for this destruction list."
        ),
        blank=True,
    )

    class Meta:
        verbose_name = _("destruction list")
        verbose_name_plural = _("destruction lists")

    def __str__(self):
        return self.name

    @transition(
        field=status, source=ListStatus.in_progress, target=ListStatus.processing
    )
    def process(self):
        pass

    @transition(field=status, source=ListStatus.processing, target=ListStatus.completed)
    def complete(self):
        self.end = timezone.now()
        self.assign(None)

    def next_assignee(self, review=None):
        assignees = self.assignees.order_by("order").all()
        first_assignee = assignees[0].assignee

        #  after author the review must always return to the first assignee
        if self.assignee == self.author:
            return first_assignee

        if not review:
            return first_assignee

        if review.status != ReviewStatus.approved:
            return self.author

        current_order = self.assignees.get(assignee=review.author).order
        next_assignee = assignees.filter(order__gt=current_order).first()
        if next_assignee:
            return next_assignee.assignee

        #  all reviews have approve status -> list is about to be completed
        return None

    def assign(self, assigned_user: Optional[User]) -> None:
        self.assignee = assigned_user
        is_reviewer = assigned_user != self.author

        if assigned_user:
            if is_reviewer:
                assignee = self.assignees.get(assignee=assigned_user)
                assignee.assigned_on = timezone.now()
                assignee.save()
                message = _("You are assigned for review.")
                email = AutomaticEmail.objects.filter(
                    type=EmailTypeChoices.review_required
                ).first()
            else:
                message = _("There is a review to process.")
                email = AutomaticEmail.objects.filter(
                    type=EmailTypeChoices.changes_required
                ).first()

            # TODO: this should only go through if the object is saved!
            Notification.objects.create(
                destruction_list=self,
                user=assigned_user,
                message=message,
            )

            if email:
                email.send(recipient=assigned_user, destruction_list=self)

    def last_review(self, reviewer=None):
        if reviewer:
            return self.reviews.filter(author=reviewer).order_by("-id").first()
        return self.reviews.order_by("-id").first()

    def list_state(self) -> dict:
        if self.status == ListStatus.completed:
            return ListStateDisplay.get_choice(ListStateDisplay.finished)

        if not self.assignee:
            return ListStateDisplay.get_choice(ListStateDisplay.approved)

        if self.assignee == self.author:
            last_review = self.last_review()
            if last_review.status == ReviewStatus.changes_requested:
                return ListStateDisplay.get_choice(ListStateDisplay.changes_requested)
            elif last_review.status == ReviewStatus.rejected:
                return ListStateDisplay.get_choice(ListStateDisplay.rejected)

        else:
            return ListStateDisplay.get_choice(ListStateDisplay.in_progress)

    def total_reviewers(self):
        return self.assignees.count()

    def completed_reviewers(self):
        if not self.assignee:
            return self.assignees.order_by("order").all().count()

        if self.assignee == self.author:
            return 0

        return (
            DestructionListAssignee.objects.get(
                assignee=self.assignee, destruction_list=self
            ).order
            - 1
        )

    def response_to_reviewer(
        self, current_reviewer
    ) -> Optional["DestructionListReviewComment"]:
        review = self.last_review(reviewer=current_reviewer)

        if review:
            comment = review.comments.last()
            return comment

    @property
    def is_review_overdue(self):
        if not self.assignee:
            return False

        archive_config = ArchiveConfig.get_solo()
        number_days = archive_config.days_until_reminder

        return self.assignees.filter(
            assignee=self.assignee,
            assignee__role__can_review_destruction=True,
            assigned_on__lt=timezone.now() - timedelta(days=number_days),
        ).exists()


class DestructionListItem(models.Model):
    destruction_list = models.ForeignKey(
        DestructionList,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("destruction list"),
    )
    zaak = models.URLField(
        _("zaak"),
        db_index=True,
        help_text=_(
            "URL-reference to the ZAAK (in Zaken API), which is planned to be destroyed."
        ),
    )
    status = FSMField(
        _("status"),
        default=ListItemStatus.suggested,
        choices=ListItemStatus.choices,
        protected=True,
        max_length=80,
    )
    extra_zaak_data = models.JSONField(
        verbose_name=_("extra zaak data"),
        help_text=_("Additional information of the zaak"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("destruction list item")
        verbose_name_plural = _("destruction list items")
        unique_together = ("destruction_list", "zaak")

    def __str__(self):
        return f"{self.destruction_list}: {self.zaak}"

    @transition(
        field=status, source=ListItemStatus.suggested, target=ListItemStatus.removed
    )
    def remove(self):
        pass

    @transition(
        field=status, source=ListItemStatus.suggested, target=ListItemStatus.processing
    )
    def process(self):
        pass

    @transition(
        field=status,
        source=ListItemStatus.processing,
        target=ListItemStatus.destroyed,
    )
    def complete(self):
        pass

    @transition(
        field=status,
        source=ListItemStatus.processing,
        target=ListItemStatus.failed,
    )
    def fail(self):
        pass


class DestructionListReview(models.Model):
    destruction_list = models.ForeignKey(
        DestructionList,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("destruction list"),
    )
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("author"),
        help_text=_("User, who performed review"),
    )
    created = models.DateTimeField(_("created"), default=timezone.now)
    text = models.TextField(
        _("text"),
        max_length=2000,
        blank=True,
        help_text=_("Review comments on the destruction list in general"),
    )
    status = models.CharField(
        _("status"), blank=True, choices=ReviewStatus.choices, max_length=80
    )
    additional_document = PrivateMediaFileField(
        verbose_name=_("additional document"),
        upload_to="reviews/%Y/%m/%d",
        help_text=_(
            "An additional document relevant for this destruction list. It will be related to the "
            "case created after the destruction list is processed."
        ),
        blank=True,
        null=True,
    )

    logs = GenericRelation(TimelineLog)

    class Meta:
        verbose_name = _("destruction list review")
        verbose_name_plural = _("destruction list reviews")

    def __str__(self):
        return f"{self.destruction_list}: {self.author}"


class DestructionListReviewComment(models.Model):
    review = models.ForeignKey(
        DestructionListReview,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("destruction list review"),
    )
    text = models.TextField(
        _("text"),
        max_length=2000,
        blank=True,
        help_text=_("Text of the comment to the review"),
    )
    created = models.DateTimeField(_("created"), default=timezone.now)

    class Meta:
        verbose_name = _("destruction list review comment")
        verbose_name_plural = _("destruction list review comments")

    def __str__(self):
        return f"Comment by {self.review.destruction_list.author} ({self.created})"


class DestructionListItemReview(models.Model):
    destruction_list_review = models.ForeignKey(
        DestructionListReview,
        on_delete=models.CASCADE,
        related_name="item_reviews",
        verbose_name=_("destruction list review"),
    )
    destruction_list_item = models.ForeignKey(
        DestructionListItem,
        on_delete=models.CASCADE,
        related_name="item_reviews",
        verbose_name=_("destruction list item"),
    )
    text = models.TextField(
        _("text"),
        max_length=2000,
        blank=True,
        help_text=_("Review comments on the destruction list item"),
    )
    suggestion = models.CharField(
        _("suggestion"), blank=True, choices=Suggestion.choices, max_length=80
    )

    class Meta:
        verbose_name = _("destruction list item review")
        verbose_name_plural = _("destruction list item reviews")
        unique_together = ("destruction_list_review", "destruction_list_item")

    def __str__(self):
        return f"({self.destruction_list_review}) - ({self.destruction_list_item})"


class DestructionListAssignee(models.Model):
    destruction_list = models.ForeignKey(
        DestructionList,
        on_delete=models.CASCADE,
        related_name="assignees",
        verbose_name=_("destruction list"),
    )
    assignee = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        verbose_name=_("assignee"),
    )
    order = models.PositiveSmallIntegerField(_("order"))
    assigned_on = models.DateTimeField(_("assigned on"), blank=True, null=True)
    reminder_sent = models.BooleanField(_("reminder sent"), default=False)

    class Meta:
        verbose_name = _("destruction list assignee")
        verbose_name_plural = _("destruction list assignees")
        unique_together = ("destruction_list", "assignee")

    def __str__(self):
        return f"{self.destruction_list}: {self.assignee}"


UUID_TEMPLATE_ELEMENT = "{{ uuid }}"
IDENTIFICATIE_TEMPLATE_ELEMENT = "{{ identificatie }}"
BRONORGANISATIE_TEMPLATE_ELEMENT = "{{ bronorganisatie }}"

ZAC_TEMPLATE_ELEMENTS = (
    UUID_TEMPLATE_ELEMENT,
    IDENTIFICATIE_TEMPLATE_ELEMENT,
    BRONORGANISATIE_TEMPLATE_ELEMENT,
)


class ArchiveConfig(SingletonModel):
    archive_date = models.DateField(
        _("archive date"),
        null=True,
        blank=True,
        help_text=_(
            "Only zaken with archiefactiedatum less that this date would be displayed for destruction"
        ),
    )
    short_review_zaaktypes = ArrayField(
        models.URLField(_("cases with short review process"), max_length=1000),
        blank=True,
        default=list,
        help_text=_(
            "Cases for which a second reviewer of the destruction list is optional"
        ),
    )
    link_to_zac = models.CharField(
        _("Link to zaakafhandelcomponent"),
        max_length=1000,
        help_text=_(
            "External link to view zaak details. Possible variables to use are: {{ uuid }}, {{ bronorganisatie }} "
            "and {{ identificatie }}. For example: https://gemeente.lan/mijnzaken/zaak/{{ uuid }}"
        ),
        blank=True,
    )
    days_until_reminder = models.PositiveIntegerField(
        _("days until reminder"),
        default=7,
        help_text=_(
            "Number of days until an email is sent reminding that the destruction list needs to be dealt with"
        ),
    )

    # Configuration for the zaak to be created once a destruction list is deleted
    create_zaak = models.BooleanField(
        _("create zaak"),
        default=False,
        help_text=_(
            "Should a case be created once a destruction list has been deleted?"
        ),
    )
    source_organisation = models.CharField(
        _("source organisation"),
        max_length=9,
        blank=True,
        help_text=_("Source organisation RSIN"),
    )
    case_type = models.URLField(
        _("case type"),
        blank=True,
        help_text=_(
            "The case type URL to use when creating the case for the destruction list deletion."
        ),
    )
    status_type = models.URLField(
        _("status type"),
        blank=True,
        help_text=_(
            "The status type URL to use when creating the case for the destruction list deletion."
        ),
    )
    result_type = models.URLField(
        _("result type"),
        blank=True,
        help_text=_(
            "The result type URL to use when creating the case for the destruction list deletion."
        ),
    )
    document_type = models.URLField(
        _("document type"),
        blank=True,
        help_text=_(
            "The document type URL to use when creating the case for the destruction list deletion."
        ),
    )
    destruction_report_downloadable = models.BooleanField(
        _("destruction report downloadable"),
        default=True,
        help_text=_(
            "Should the destruction report be downloadable through the application?"
        ),
    )
    additional_review_document_type = models.URLField(
        _("Additional review document type"),
        blank=True,
        help_text=_(
            "The document type URL to use for documents which were uploaded by the "
            "reviewers during the review process."
        ),
    )

    class Meta:
        verbose_name = _("archive configuration")


class StandardReviewAnswer(OrderedModel):
    reason = models.CharField(
        verbose_name=_("reason"),
        max_length=200,
        help_text=_(
            "Reason for the reviewer to request changes to a destruction list."
        ),
    )

    class Meta(OrderedModel.Meta):
        verbose_name = _("standard review answers")
        verbose_name_plural = _("standard review answers")
