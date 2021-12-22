from typing import List, Tuple

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import models, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

from django_filters.views import FilterView
from extra_views import CreateWithInlinesView, InlineFormSetFactory
from timeline_logger.models import TimelineLog

from archiefbeheercomponent.accounts.mixins import RoleRequiredMixin
from archiefbeheercomponent.notifications.models import Notification

from ...constants import RoleTypeChoices
from ..filters import ReviewerListFilter
from ..forms import ReviewForm, ReviewItemBaseForm
from ..models import (
    ArchiveConfig,
    DestructionList,
    DestructionListItemReview,
    DestructionListReview,
    StandardReviewAnswer,
)
from ..tasks import process_destruction_list

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

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        config = ArchiveConfig.get_solo()
        context.update({"can_download_report": config.destruction_report_downloadable})
        return context


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
