from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Use the built-in user model.
    """

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_("Required. 150 characters or fewer."),
        error_messages={"unique": _("A user with that username already exists."),},
    )
    first_name = models.CharField(_("first name"), max_length=255, blank=True)
    last_name = models.CharField(_("last name"), max_length=255, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("role"),
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name


class Role(models.Model):
    name = models.CharField(
        _("name"), max_length=255, unique=True, help_text=_("Name of the role")
    )
    organisatie_onderdeel = models.URLField(_("organisatie onderdeel"), blank=True)
    can_start_destruction = models.BooleanField(
        _("can start destruction"),
        default=False,
        help_text=_(
            'Designates whether people in this role can create a "vernietigingslijst", which is the '
            'starting point for the "records destruction" process.'
        ),
    )
    can_review_destruction = models.BooleanField(
        _("can review destruction"),
        default=False,
        help_text=_(
            "Designates if people in this role can review created record destruction lists and approve/reject them."
        ),
    )
    can_view_case_details = models.BooleanField(
        _("can view case details"),
        default=False,
        help_text=_(
            "Designates whether people in this role can view the contents of zaken listed on the "
            "record destruction lists."
        ),
    )

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")

    def __str__(self):
        return self.name
