from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from timeline_logger.views import TimelineLogListView


class AuditTrailView(LoginRequiredMixin, UserPassesTestMixin, TimelineLogListView):
    def test_func(self) -> bool:
        return self.request.user.is_superuser
