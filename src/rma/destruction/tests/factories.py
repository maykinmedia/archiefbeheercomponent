import factory

from rma.accounts.tests.factories import UserFactory


class DestructionListFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    author = factory.SubFactory(UserFactory)

    class Meta:
        model = "destruction.DestructionList"


class DestructionListItemFactory(factory.django.DjangoModelFactory):
    destruction_list = factory.SubFactory(DestructionListFactory)
    zaak = factory.Faker("url")

    class Meta:
        model = "destruction.DestructionListItem"
