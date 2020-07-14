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


class AuthorOrAssigneeRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def get_destruction_list(self):
        raise NotImplementedError(
            "'get_destruction_list method' must be overriden in subclass"
        )

    def test_func(self):
        if not self.request.user.role:
            return False

        destruction_list = self.get_destruction_list()
        is_author = destruction_list.author == self.request.user
        is_assignee = destruction_list.assignees.filter(
            assignee=self.request.user
        ).exists()

        if is_author or is_assignee:
            return True

        return False
