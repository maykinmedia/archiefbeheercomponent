from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    role_permission = None

    def test_func(self):
        if not self.role_permission:
            return False

        role = self.request.user.role
        if role is None:
            return False
        return getattr(role, self.role_permission)
