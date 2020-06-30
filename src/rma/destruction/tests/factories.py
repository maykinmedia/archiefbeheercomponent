import factory
import factory.fuzzy

from rma.accounts.tests.factories import UserFactory

from ..constants import ReviewStatus


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


class DestructionListReviewFactory(factory.django.DjangoModelFactory):
    destruction_list = factory.SubFactory(DestructionListFactory)
    author = factory.SubFactory(UserFactory)
    text = factory.Faker("text")
    status = factory.fuzzy.FuzzyChoice(choices=ReviewStatus.values)

    class Meta:
        model = "destruction.DestructionListReview"
