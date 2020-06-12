import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

logger = logging.getLogger(__name__)


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    role_permission = None

    def test_func(self):
        if not self.role_permission:
            logger.debug("no 'role_permission' is set for %r", self)
            return False

        role = self.request.user.role
        if role is None:
            return False
        return getattr(role, self.role_permission)
