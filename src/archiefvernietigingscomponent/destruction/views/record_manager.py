import logging
from datetime import date

from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from django_filters.views import FilterView
from extra_views import InlineFormSetFactory, UpdateWithInlinesView
from furl import furl
from timeline_logger.models import TimelineLog
from zds_client.client import ClientError

from archiefvernietigingscomponent.accounts.mixins import (
    AuthorOrAssigneeRequiredMixin,
    RoleRequiredMixin,
)
from archiefvernietigingscomponent.notifications.models import Notification

from ..constants import ListItemStatus, ListStatus, Suggestion
from ..filters import RecordManagerListFilter
from ..forms import (
    DestructionListForm,
    ListItemForm,
    ReviewCommentForm,
    ZaakArchiveDetailsForm,
    ZaakUrlForm,
    get_reviewer_choices,
    get_zaaktype_choices,
)
from ..models import (
    ArchiveConfig,
    DestructionList,
    DestructionListItem,
    DestructionListReviewComment,
)
from ..service import fetch_zaak
from ..tasks import update_zaak, update_zaken

logger = logging.getLogger(__name__)

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
        current_date = archive_config.archive_date or timezone.now().date()

        # add zaaktypen
        context.update(
            {
                "zaaktypen": get_zaaktype_choices(),
                "reviewers": get_reviewer_choices(self.request.user),
                "short_review_zaaktypes": archive_config.short_review_zaaktypes,
                "current_date": current_date.isoformat(),
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

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        # add zaaktypen
        context.update({"zaaktypen": get_zaaktype_choices()})
        return context


class UpdateZaakArchiveDetailsView(SuccessMessageMixin, RoleRequiredMixin, FormView):
    template_name = "destruction/update_zaak_archive_details.html"
    role_permission = "can_start_destruction"
    form_class = ZaakArchiveDetailsForm
    success_message = _("Archiving details successfully updated!")

    _zaak = None

    def get_success_url(self):
        return_url = furl(reverse("destruction:update-zaak-archive-details"))
        return_url.args["url"] = self.zaak["url"]
        return return_url.url

    @property
    def zaak(self):
        if not self._zaak:
            form = ZaakUrlForm(data=self.request.GET)

            if not form.is_valid():
                raise PermissionDenied("No zaak URL provided.")

            full_zaak = fetch_zaak(form.cleaned_data["url"])
            needed_fields = [
                "url",
                "identificatie",
                "archiefnominatie",
                "archiefactiedatum",
                "archiefstatus",
            ]
            self._zaak = {field: full_zaak.get(field) for field in needed_fields}
        return self._zaak

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context.update({"zaak": self.zaak})
        return context

    def get_initial(self):
        initial_data = super().get_initial()

        form = self.form_class(data=self.zaak)
        if form.is_valid():
            initial_data.update(form.cleaned_data)
        return initial_data

    def form_valid(self, form):
        updated_data = {}
        fields = ["archiefnominatie", "archiefstatus", "archiefactiedatum"]
        for field in fields:
            if value := form.cleaned_data.get(field):
                if isinstance(value, date):
                    value = value.isoformat()
                updated_data[field] = value

        try:
            update_zaak(
                form.cleaned_data["url"],
                updated_data,
                audit_comment=form.cleaned_data["comment"],
            )
        except ClientError as exc:
            # The client raised a 4xx error
            form.add_error(
                field=None,
                error=_("An error has occurred. The case could not be updated."),
            )
            self.parse_errors(exc, form)
            return super().form_invalid(form)

        return super().form_valid(form)

    @staticmethod
    def parse_errors(exc, form):
        error = exc.args[0]

        try:
            for param in error["invalidParams"]:
                field_name = param["name"]
                if field_name == "nonFieldErrors":
                    field_name = None

                form.add_error(
                    field=field_name, error=param["reason"],
                )
        except KeyError as err:
            logger.error("Encountered missing key %s in ClientError: %s", err, exc)
