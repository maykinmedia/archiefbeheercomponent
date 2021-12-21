from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView

from ..models import DestructionList

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
