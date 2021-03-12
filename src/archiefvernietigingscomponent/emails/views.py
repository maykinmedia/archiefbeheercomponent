from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from archiefvernietigingscomponent.emails.models import EmailPreference


class EmailPreferenceUpdateView(UserPassesTestMixin, UpdateView):
    model = EmailPreference
    fields = ("preference",)
    success_url = reverse_lazy("entry")

    def test_func(self):
        email_preference = self.get_object()

        if self.request.user == email_preference.user:
            return True

        return False
