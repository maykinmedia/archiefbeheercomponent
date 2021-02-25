from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_fsm import FSMField, transition
from solo.models import SingletonModel
from timeline_logger.models import TimelineLog

from archiefvernietigingscomponent.notifications.models import Notification

from .constants import ListItemStatus, ListStatus, ReviewStatus, Suggestion
from .query import DestructionListQuerySet


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

    objects = DestructionListQuerySet.as_manager()

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

        if review.status == ReviewStatus.changes_requested:
            return self.author

        current_order = self.assignees.get(assignee=review.author).order
        next_assignee = assignees.filter(order__gt=current_order).first()
        if next_assignee:
            return next_assignee.assignee

        #  all reviews have approve status -> list is about to be completed
        return None

    def assign(self, assignee):
        self.assignee = assignee
        is_reviewer = assignee != self.author

        if assignee:
            if is_reviewer:
                message = _("You are assigned for review.")
            else:
                message = _("There is a review to process.")

            # TODO: this should only go through if the object is saved!
            Notification.objects.create(
                destruction_list=self, user=assignee, message=message,
            )

    def last_review(self):
        return self.reviews.order_by("-id").first()


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
    extra_zaak_data = JSONField(
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
        field=status, source=ListItemStatus.processing, target=ListItemStatus.destroyed,
    )
    def complete(self):
        pass

    @transition(
        field=status, source=ListItemStatus.processing, target=ListItemStatus.failed,
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
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        verbose_name=_("author"),
        help_text=_("User who added the comment to the review"),
    )
    created = models.DateTimeField(_("created"), default=timezone.now)

    class Meta:
        verbose_name = _("destruction list review comment")
        verbose_name_plural = _("destruction list review comments")

    def __str__(self):
        return f"Comment by {self.author} ({self.created})"


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
        "accounts.User", on_delete=models.PROTECT, verbose_name=_("assignee"),
    )
    order = models.PositiveSmallIntegerField(_("order"))

    class Meta:
        verbose_name = _("destruction list assignee")
        verbose_name_plural = _("destruction list assignees")
        unique_together = ("destruction_list", "assignee")

    def __str__(self):
        return f"{self.destruction_list}: {self.assignee}"


class ArchiveConfig(SingletonModel):
    archive_date = models.DateField(
        _("archive date"),
        null=True,
        blank=True,
        help_text=_(
            "Only zaken with archiefactiedatum less that this date would be displayed for destruction"
        ),
    )

    class Meta:
        verbose_name = _("archive configuration")
