from django.db.models.base import ModelBase
from django.db.models.signals import post_save
from django.dispatch import receiver

from archiefbeheercomponent.accounts.models import User
from archiefbeheercomponent.emails.models import EmailPreference


@receiver(post_save, sender=User)
def relate_email_preference_to_user(
    sender: ModelBase, instance: User, created: bool, **kwargs
) -> None:
    """Create an object to store the email preferences of a User"""

    if created and not EmailPreference.objects.filter(user=instance).exists():
        EmailPreference.objects.create(user=instance)
