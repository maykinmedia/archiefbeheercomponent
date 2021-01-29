"""
WSGI config for Archiefvernietingscomponent project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

from archiefvernietingscomponent.setup import setup_env

setup_env()

application = get_wsgi_application()
