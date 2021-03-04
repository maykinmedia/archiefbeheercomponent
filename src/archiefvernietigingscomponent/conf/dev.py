import os
import warnings

from .includes.environ import config

os.environ.setdefault("DEBUG", "yes")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1")
os.environ.setdefault(
    "SECRET_KEY", "145cqii@)+z$b&9dcmdctpm+&be1#9zslxm+x)0+u*^qf!qz(6"
)
os.environ.setdefault("IS_HTTPS", "no")

# uses postgresql by default, see base.py
os.environ.setdefault("DB_NAME", "archiefvernietigingscomponent"),
os.environ.setdefault("DB_USER", "archiefvernietigingscomponent"),
os.environ.setdefault("DB_PASSWORD", "archiefvernietigingscomponent"),

os.environ.setdefault("SENDFILE_BACKEND", "django_sendfile.backends.development")

from .includes.base import *  # noqa isort:skip

#
# Standard Django settings.
#
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING["loggers"].update(
    {
        "archiefvernietigingscomponent": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django": {"handlers": ["console"], "level": "DEBUG", "propagate": True,},
        "django.db.backends": {
            "handlers": ["django"],
            "level": "DEBUG",
            "propagate": False,
        },
        "performance": {"handlers": ["console"], "level": "INFO", "propagate": True,},
        #
        # See: https://code.djangoproject.com/ticket/30554
        # Autoreload logs excessively, turn it down a bit.
        #
        "django.utils.autoreload": {
            "handlers": ["django"],
            "level": "INFO",
            "propagate": False,
        },
    }
)

#
# Library settings
#

# Django debug toolbar
INSTALLED_APPS += [
    "debug_toolbar",
]
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
INTERNAL_IPS = ("127.0.0.1",)
DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}

AXES_BEHIND_REVERSE_PROXY = (
    False  # Default: False (we are typically using Nginx as reverse proxy)
)

# in memory cache and django-axes don't get along.
# https://django-axes.readthedocs.io/en/latest/configuration.html#known-configuration-problems
if not config("USE_REDIS_CACHE", default=False):
    CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
        "axes": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
        "oas": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    }

# THOU SHALT NOT USE NAIVE DATETIMES
warnings.filterwarnings(
    "error",
    r"DateTimeField .* received a naive datetime",
    RuntimeWarning,
    r"django\.db\.models\.fields",
)

#
# Custom settings
#
ENVIRONMENT = "development"

#
# Django Solo
#
SOLO_CACHE_TIMEOUT = 0

# Override settings with local settings.
try:
    from .includes.local import *  # noqa
except ImportError:
    pass
