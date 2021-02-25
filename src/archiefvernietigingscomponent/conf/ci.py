"""
Continuous integration settings module.
"""
import logging
import os
import warnings

os.environ.setdefault("SECRET_KEY", "dummy")
os.environ.setdefault("IS_HTTPS", "no")

from .includes.base import *  # noqa isort:skip

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    # https://github.com/jazzband/django-axes/blob/master/docs/configuration.rst#cache-problems
    "axes": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
    "oas": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

LOGGING = None  # Quiet is nice
logging.disable(logging.CRITICAL)

ENVIRONMENT = "ci"

#
# Django-axes
#
AXES_BEHIND_REVERSE_PROXY = False

# THOU SHALT NOT USE NAIVE DATETIMES
warnings.filterwarnings(
    "error",
    r"DateTimeField .* received a naive datetime",
    RuntimeWarning,
    r"django\.db\.models\.fields",
)
