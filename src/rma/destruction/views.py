from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView
from django.views.generic.base import RedirectView

from django_filters.views import FilterView
from extra_views import (
    CreateWithInlinesView,
    InlineFormSetFactory,
    UpdateWithInlinesView,
)
from timeline_logger.models import TimelineLog

from rma.accounts.mixins import RoleRequiredMixin
from rma.notifications.models import Notification

from .filters import ReviewerListFilter
from .forms import (
    DestructionListForm,
    ReviewForm,
    ReviewItemBaseFormset,
    get_reviewer_choices,
    get_zaaktype_choices,
)
from .models import (
    DestructionList,
    DestructionListItem,
    DestructionListItemReview,
    DestructionListReview,
)
from .tasks import process_destruction_list


class EnterView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        role = self.request.user.role
        if role and role.can_start_destruction:
            return reverse("destruction:record-manager-list")

        if role and role.can_review_destruction:
            return reverse("destruction:reviewer-list")

        if self.request.user.is_superuser:
            return reverse("audit:audit-trail")

        raise PermissionDenied(self.get_permission_denied_message())


class RecordManagerDestructionListView(RoleRequiredMixin, ListView):
    """ data for user who can start destruction lists"""

    role_permission = "can_start_destruction"
    template_name = "destruction/recordmanager_list.html"

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

        # add zaaktypen
        context.update(
            {
                "zaaktypen": get_zaaktype_choices(),
                "reviewers": get_reviewer_choices(self.request.user),
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
            template="destruction/logs/created.txt",
            n_items=destruction_list.items.count(),
            reviewers=list(
                destruction_list.assignees.values("assignee__id", "assignee__username")
            ),
        )

        return response


class ReviewerDestructionListView(RoleRequiredMixin, FilterView):
    """ data for user who can reviewer destruction lists"""

    role_permission = "can_review_destruction"
    template_name = "destruction/reviewer_list.html"
    filterset_class = ReviewerListFilter

    def get_queryset(self):
        review_status = DestructionListReview.objects.filter(
            author=self.request.user, destruction_list=models.OuterRef("id")
        ).values("status")

        prefiltered_qs = DestructionList.objects.filter(
            assignee=self.request.user
        ) | DestructionList.objects.reviewed_by(self.request.user)

        return prefiltered_qs.annotate(
            review_status=models.Subquery(review_status[:1])
        ).order_by("-created")


class ReviewItemInline(InlineFormSetFactory):
    model = DestructionListItemReview
    fields = ["destruction_list_item", "text", "suggestion"]
    formset_class = ReviewItemBaseFormset


class ReviewCreateView(RoleRequiredMixin, UserPassesTestMixin, CreateWithInlinesView):
    model = DestructionListReview
    form_class = ReviewForm
    inlines = [ReviewItemInline]
    template_name = "destruction/review_create.html"
    success_url = reverse_lazy("destruction:reviewer-list")
    role_permission = "can_review_destruction"

    def test_func(self):
        destruction_list = self.get_destruction_list()
        if not destruction_list.assignees.filter(assignee=self.request.user).exists():
            return False

        return True

    def get_destruction_list(self):
        list_id = self.kwargs.get("destruction_list")

        return get_object_or_404(DestructionList, pk=int(list_id))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset = context["inlines"][0]

        destruction_list = self.get_destruction_list()
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
            }
        )
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.destruction_list = self.get_destruction_list()

        return super().form_valid(form)

    @transaction.atomic
    def forms_valid(self, form, inlines):
        response = super().forms_valid(form, inlines)

        # log review
        list_review = form.instance
        TimelineLog.log_from_request(
            self.request,
            list_review,
            template="destruction/logs/review_created.txt",
            n_items=list_review.item_reviews.count(),
        )
        # send notification
        Notification.objects.create(
            destruction_list=list_review.destruction_list,
            user=list_review.destruction_list.author,
            message=_("Destruction list has been reviewed by %(author)s")
            % {"author": list_review.author},
        )

        destruction_list = self.get_destruction_list()
        destruction_list.assign(destruction_list.next_assignee(list_review))
        destruction_list.save()

        if not destruction_list.assignee:
            transaction.on_commit(
                lambda: process_destruction_list.delay(destruction_list.id)
            )

        return response


class DestructionListItemInline(InlineFormSetFactory):
    model = DestructionListItem
    fields = ["status"]


class DestructionListDetailView(RoleRequiredMixin, UpdateWithInlinesView):
    model = DestructionList
    fields = []
    inlines = [DestructionListItemInline]
    template_name = "destruction/destructionlist_detail.html"
    success_url = reverse_lazy("destruction:record-manager-list")
    role_permission = "can_start_destruction"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset = context["inlines"][0]

        context.update(
            {
                "formset_config": {
                    "prefix": formset.prefix,
                    **{
                        field.name: int(field.value())
                        for field in formset.management_form
                    },
                },
            }
        )
        return context
