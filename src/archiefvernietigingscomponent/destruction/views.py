from typing import List, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic.base import RedirectView, TemplateView

from django_filters.views import FilterView
from extra_views import (
    CreateWithInlinesView,
    InlineFormSetFactory,
    UpdateWithInlinesView,
)
from timeline_logger.models import TimelineLog

from archiefvernietigingscomponent.accounts.mixins import (
    AuthorOrAssigneeRequiredMixin,
    RoleRequiredMixin,
)
from archiefvernietigingscomponent.notifications.models import Notification

from ..constants import RoleTypeChoices
from .constants import ListItemStatus, ListStatus, Suggestion
from .filters import RecordManagerListFilter, ReviewerListFilter
from .forms import (
    DestructionListForm,
    ListItemForm,
    ReviewCommentForm,
    ReviewForm,
    ReviewItemBaseForm,
    get_reviewer_choices,
    get_zaaktype_choices,
)
from .models import (
    ArchiveConfig,
    DestructionList,
    DestructionListItem,
    DestructionListItemReview,
    DestructionListReview,
    DestructionListReviewComment,
    StandardReviewAnswer,
)
from .tasks import process_destruction_list, update_zaken

# Views that route to the appriopriate specialized view


class EnterView(LoginRequiredMixin, RedirectView):
    login_url = reverse_lazy("start-page")

    def get_redirect_url(self, *args, **kwargs):
        role = self.request.user.role
        if role and role.can_start_destruction:
            return reverse("destruction:record-manager-list")

        if role and role.can_review_destruction:
            return reverse("destruction:reviewer-list")

        if self.request.user.is_superuser:
            return reverse("audit:audit-trail")

        raise PermissionDenied(self.get_permission_denied_message())


class DestructionListRedirectView(LoginRequiredMixin, RedirectView):
    """
    Redirect the end user to the appropriate detail view for the DL.

    Authors go to the :class:`DestructionListDetailView`, while reviewers go to the
    review page. Anyone else gets a 403.
    """

    def get_redirect_url(self, *args, **kwargs) -> str:
        qs = DestructionList.objects.select_related("author")
        destruction_list = get_object_or_404(qs, pk=kwargs["pk"])

        if destruction_list.author == self.request.user:
            return reverse(
                "destruction:record-manager-detail", kwargs={"pk": destruction_list.pk}
            )

        permission_denied = PermissionDenied(self.get_permission_denied_message())

        # not an assignee, you have no business hitting this URL!
        if not destruction_list.assignees.filter(assignee=self.request.user).exists():
            raise permission_denied

        # okay, you're an assignee, are you also THE assignee?
        if destruction_list.assignee == self.request.user:
            return reverse(
                "destruction:reviewer-create",
                kwargs={"destruction_list": destruction_list.id},
            )

        # all the rest -> denied!
        raise permission_denied


# Record manager views


class RecordManagerDestructionListView(RoleRequiredMixin, FilterView):
    """ data for user who can start destruction lists"""

    role_permission = "can_start_destruction"
    template_name = "destruction/recordmanager_list.html"
    filterset_class = RecordManagerListFilter
    paginate_by = 20

    def get_queryset(self):
        return DestructionList.objects.filter(author=self.request.user).order_by("-id")


class DestructionListCreateView(RoleRequiredMixin, CreateView):
    model = DestructionList
    form_class = DestructionListForm
    template_name = "destruction/destructionlist_create.html"
    success_url = reverse_lazy("destruction:record-manager-list")
    role_permission = "can_start_destruction"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        archive_config = ArchiveConfig.get_solo()

        # add zaaktypen
        context.update(
            {
                "zaaktypen": get_zaaktype_choices(),
                "reviewers": get_reviewer_choices(self.request.user),
                "short_review_zaaktypes": archive_config.short_review_zaaktypes,
            }
        )

        return context

    @transaction.atomic
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        destruction_list = form.instance

        # log
        TimelineLog.log_from_request(
            self.request,
            destruction_list,
            template="destruction/logs/created.html",
            n_items=destruction_list.items.count(),
            reviewers=list(
                destruction_list.assignees.values("assignee__id", "assignee__username")
            ),
            items=form.cleaned_data["zaken_identificaties"],
        )

        return response


class DestructionListItemInline(InlineFormSetFactory):
    model = DestructionListItem
    form_class = ListItemForm


class DestructionListDetailView(AuthorOrAssigneeRequiredMixin, UpdateWithInlinesView):
    model = DestructionList
    fields = []
    inlines = [DestructionListItemInline]
    template_name = "destruction/destructionlist_detail.html"
    success_url = reverse_lazy("destruction:record-manager-list")

    def get_destruction_list(self):
        return self.get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        formset = context["inlines"][0]
        dl = self.get_object()
        can_update = (
            self.request.user == dl.assignee == dl.author
            and dl.status != ListStatus.completed
        )
        can_abort = self.request.user == dl.author and dl.status != ListStatus.completed

        if can_update and "comment_form" not in context:
            context["comment_form"] = ReviewCommentForm()

        context.update(
            {
                "formset_config": {
                    "prefix": formset.prefix,
                    **{
                        field.name: int(field.value())
                        for field in formset.management_form
                    },
                },
                "can_update": can_update,
                "can_abort": can_abort,
            }
        )
        return context

    def abort_destruction_list(self, destruction_list):
        list_items = destruction_list.items.filter(status=ListItemStatus.suggested)
        for list_item in list_items:
            list_item.remove()
            list_item.save()

        assignee = destruction_list.assignee

        destruction_list.process()
        destruction_list.complete()
        destruction_list.save()

        TimelineLog.log_from_request(
            self.request,
            destruction_list,
            template="destruction/logs/aborted.html",
            n_items=destruction_list.items.count(),
        )

        # If the author is not assigned to the list, notify the assignee
        # that the list has been aborted.
        if assignee and destruction_list.author != assignee:
            message = _(
                "%(author)s has aborted the destruction list. No further action is required."
            ) % {"author": destruction_list.author}
            Notification.objects.create(
                destruction_list=destruction_list, user=assignee, message=message,
            )

    @transaction.atomic
    def forms_valid(self, form, inlines):
        response = super().forms_valid(form, inlines)

        destruction_list = form.instance

        if "abort" in self.request.POST:
            if destruction_list.status == ListStatus.completed:
                return HttpResponseBadRequest(
                    _(
                        "The destruction of this list can't be aborted because it has already been completed."
                    )
                )

            self.abort_destruction_list(destruction_list)
            return response

        # Check if there are comments from the author
        comment_text = None
        if self.request.POST.get("text"):
            comment = DestructionListReviewComment(
                review=destruction_list.last_review()
            )
            comment_form = ReviewCommentForm(self.request.POST, instance=comment)
            if comment_form.is_valid():
                comment_form.save()
            else:
                super().forms_invalid(form, inlines)

            comment_text = comment_form.cleaned_data["text"]

        # Get the identificaties of the removed zaken
        removed_zaken = []
        for list_item_form in inlines[0]:
            action = list_item_form.cleaned_data.get("action")
            if action:
                removed_zaken.append(list_item_form.cleaned_data["identificatie"])

        # log
        TimelineLog.log_from_request(
            self.request,
            destruction_list,
            template="destruction/logs/updated.html",
            n_items=len(removed_zaken),
            text=comment_text if comment_text else "",
            items=removed_zaken,
        )

        # assign a reviewer
        destruction_list.assign(destruction_list.next_assignee())
        destruction_list.save()

        # update zaken
        update_data = []
        list_item_formset = inlines[0]
        for list_item_form in list_item_formset:
            list_item = list_item_form.instance
            action = list_item_form.cleaned_data.get("action")
            if action == Suggestion.change_and_remove:
                archive_data = {
                    "archiefnominatie": list_item_form.cleaned_data["archiefnominatie"],
                    "archiefactiedatum": list_item_form.cleaned_data[
                        "archiefactiedatum"
                    ],
                }
                update_data.append((list_item.id, archive_data))

        if update_data:
            transaction.on_commit(lambda: update_zaken.delay(update_data))

        return response


class ZakenWithoutArchiveDateView(RoleRequiredMixin, TemplateView):
    template_name = "destruction/zaken_without_archive_date_list.html"
    role_permission = "can_start_destruction"


# Reviewer views


class ReviewerDestructionListView(RoleRequiredMixin, FilterView):
    """ data for user who can reviewer destruction lists"""

    role_permission = "can_review_destruction"
    template_name = "destruction/reviewer_list.html"
    filterset_class = ReviewerListFilter
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        review_status = DestructionListReview.objects.filter(
            author=user, destruction_list=models.OuterRef("id")
        ).values("status")

        prefiltered_qs = DestructionList.objects.filter(
            Q(assignee=user) | Q(reviews__author=user)
        ).distinct()

        return prefiltered_qs.annotate(
            review_status=models.Subquery(review_status[:1])
        ).order_by("-created")


class ReviewItemInline(InlineFormSetFactory):
    model = DestructionListItemReview
    form_class = ReviewItemBaseForm


class ReviewCreateView(RoleRequiredMixin, UserPassesTestMixin, CreateWithInlinesView):
    model = DestructionListReview
    form_class = ReviewForm
    inlines = [ReviewItemInline]
    template_name = "destruction/review_create.html"
    success_url = reverse_lazy("destruction:reviewer-list")
    role_permission = "can_review_destruction"

    def test_func(self):
        allowed = super().test_func()
        if allowed is False:
            return allowed

        destruction_list = self.get_destruction_list()
        if not destruction_list.assignees.filter(assignee=self.request.user).exists():
            return False

        return True

    def get_destruction_list(self):
        list_id = self.kwargs.get("destruction_list")
        return get_object_or_404(DestructionList, pk=list_id)

    def get_formatted_standard_review_reasons(self) -> List[Tuple[str, str]]:
        answers = StandardReviewAnswer.objects.all().order_by("order")
        return [(answer.reason, answer.reason) for answer in answers]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset = context["inlines"][0]

        destruction_list = self.get_destruction_list()
        standard_review_choices = self.get_formatted_standard_review_reasons()
        context.update(
            {
                "destruction_list": destruction_list,
                "destruction_list_json": {
                    "name": destruction_list.name,
                    "author": destruction_list.author.get_full_name(),
                    "created": timesince(destruction_list.created),
                },
                "formset_config": {
                    "prefix": formset.prefix,
                    **{
                        field.name: int(field.value())
                        for field in formset.management_form
                    },
                },
                "show_optional_columns": (
                    not destruction_list.contains_sensitive_info
                    or self.request.user.role.type != RoleTypeChoices.archivist
                ),
                "standard_review_choices": standard_review_choices,
            }
        )

        # If the current reviewer has previously requested changes,
        # add any comments that the user has made when addressing those changes
        current_reviewer = self.request.user
        comment = destruction_list.response_to_reviewer(current_reviewer)

        if comment:
            comment_author = comment.review.destruction_list.author
            context["comment_to_review"] = {
                "author": comment_author.get_full_name(),
                "text": comment.text,
            }

        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.destruction_list = self.get_destruction_list()

        return super().form_valid(form)

    @transaction.atomic
    def forms_valid(self, form, inlines):
        response = super().forms_valid(form, inlines)

        # Get the identificaties of the zaken with suggestions
        zaken_with_suggestions = []
        for list_item_form in inlines[0]:
            suggestion = list_item_form.cleaned_data.get("suggestion")
            if suggestion:
                zaken_with_suggestions.append(
                    list_item_form.cleaned_data["identificatie"]
                )

        # log review
        list_review = form.instance
        TimelineLog.log_from_request(
            self.request,
            list_review,
            template="destruction/logs/review_created.html",
            n_items=len(zaken_with_suggestions),
            text=list_review.text,
            items=zaken_with_suggestions,
        )
        # send notification
        message = _("{author} has reviewed the destruction list.").format(
            author=list_review.author
        )
        Notification.objects.create(
            destruction_list=list_review.destruction_list,
            user=list_review.destruction_list.author,
            message=message,
        )

        destruction_list = self.get_destruction_list()
        destruction_list.assign(destruction_list.next_assignee(list_review))
        destruction_list.save()

        if not destruction_list.assignee:
            transaction.on_commit(
                lambda: process_destruction_list.delay(destruction_list.id)
            )

        return response
