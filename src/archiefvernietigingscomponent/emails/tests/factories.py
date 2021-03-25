import factory

from archiefvernietigingscomponent.emails.constants import EmailTypeChoices


class AutomaticEmailFactory(factory.django.DjangoModelFactory):
    type = EmailTypeChoices.review_required
    subject = factory.Faker("bs")
    body = factory.Faker("text")

    class Meta:
        model = "emails.AutomaticEmail"
