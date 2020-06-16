from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView
from django.views.generic.base import RedirectView

from rma.accounts.mixins import RoleRequiredMixin

from .forms import DestructionListForm, get_zaaktype_choices
from .models import DestructionList


class EnterView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        role = self.request.user.role
        if role and role.can_start_destruction:
            return reverse("destruction:record-manager-list")

        raise PermissionDenied(self.get_permission_denied_message())


class RecordManagerDestructionListView(RoleRequiredMixin, ListView):
    """ data for user who can start destruction lists"""

    role_permission = "can_start_destruction"
    template_name = "destruction/recordmanager_list.html"

    def get_queryset(self):
        return DestructionList.objects.filter(author=self.request.user).order_by("-id")


class DestructionListCreateView(CreateView):
    model = DestructionList
    form_class = DestructionListForm
    template_name = "destruction/destructionlist_create.html"
    success_url = reverse_lazy("destruction:record-manager-list")

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        # add zaaktypen
        context.update({"zaaktypen": get_zaaktype_choices()})

        return context

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)
