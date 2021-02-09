import re

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel

color_re = re.compile(r"^[0-9a-fA-F]+")
validate_color = RegexValidator(
    color_re,
    # Translators: "letters" means latin letters: a-z and A-Z.
    _("Enter a valid HTML color code value consisting of only hexidecimal characters."),
    "invalid",
)


class ThemeConfig(SingletonModel):
    logo = models.FileField(
        upload_to="theme/",
        help_text=_(
            "Image will be scaled down to a height of 100 pixels. Typically upload a picture with a height of 200 pixels."
        ),
    )

    organization_name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=400, blank=True)

    color_primary = models.CharField(
        max_length=6, default="04a5bb", validators=[validate_color]
    )
    color_primary_light = models.CharField(
        max_length=6, default="C3eaef", validators=[validate_color]
    )
    color_secondary = models.CharField(
        max_length=6, default="017092", validators=[validate_color]
    )

    color_link = models.CharField(
        max_length=6, default="017092", validators=[validate_color]
    )
    color_link_dark = models.CharField(
        max_length=6, default="051f31", validators=[validate_color]
    )

    class Meta:
        verbose_name = _("Theme configuration")
