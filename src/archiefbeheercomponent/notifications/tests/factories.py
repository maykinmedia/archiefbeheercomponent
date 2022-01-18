import factory

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.destruction.tests.factories import DestructionListFactory


class NotificationFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    destruction_list = factory.SubFactory(DestructionListFactory)
    message = factory.Faker("text")

    class Meta:
        model = "notifications.Notification"
