import re

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel

color_re = re.compile(r"^[0-9a-fA-F]+")
validate_color = RegexValidator(
    color_re,
    _("Enter a valid HTML color code value consisting of only hexidecimal characters."),
    "invalid",
)


class ThemeConfig(SingletonModel):
    logo = models.FileField(
        upload_to="theme/",
        help_text=_(
            "Image will be scaled down to a height of 100 pixels. "
            "Typically upload a picture with a height of 200 pixels."
        ),
    )

    organization_name = models.CharField(
        _("Organization name"),
        max_length=100,
        help_text=_("Shown at the top of the footer."),
    )
    tagline = models.CharField(
        _("Tagline"),
        max_length=200,
        blank=True,
        help_text=_("Shown just below the organization name in the footer."),
    )
    phone_number = models.CharField(
        _("Phone number"),
        max_length=50,
        blank=True,
        help_text=_("Shown below the tagline in the footer."),
    )
    address = models.CharField(
        _("Address"),
        max_length=400,
        blank=True,
        help_text=_(
            "Shown as an address section at the bottom of the footer. Newlines are supported."
        ),
    )

    color_primary = models.CharField(
        _("Primary color"),
        max_length=6,
        default="04a5bb",
        validators=[validate_color],
        help_text=_("The main color used for footer and buttons."),
    )
    color_primary_light = models.CharField(
        _("Primary color (light)"),
        max_length=6,
        default="C3eaef",
        validators=[validate_color],
        help_text=_("Used in places where the main color is too dark."),
    )
    color_secondary = models.CharField(
        _("Secondary color"),
        max_length=6,
        default="017092",
        validators=[validate_color],
        help_text=_(
            "Typically a darker shade or contrasting color of the primary color, used for button hover states, "
            "panel headers and outlines."
        ),
    )

    color_link = models.CharField(
        _("Link color"),
        max_length=6,
        default="017092",
        validators=[validate_color],
        help_text=_("The main link color."),
    )
    color_link_dark = models.CharField(
        _("Link color (dark)"),
        max_length=6,
        default="051f31",
        validators=[validate_color],
        help_text=_(
            "Typically a darker shade of the link color, used for hover states."
        ),
    )

    class Meta:
        verbose_name = _("Theme configuration")
