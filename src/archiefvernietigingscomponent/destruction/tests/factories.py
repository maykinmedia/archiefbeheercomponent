import factory
import factory.fuzzy

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory

from ..constants import ReviewStatus, Suggestion


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


class DestructionListReviewCommentFactory(factory.django.DjangoModelFactory):
    text = factory.Faker("text")
    review = factory.SubFactory(DestructionListReviewFactory)

    class Meta:
        model = "destruction.DestructionListReviewComment"


class DestructionListItemReviewFactory(factory.django.DjangoModelFactory):
    destruction_list_item = factory.SubFactory(DestructionListItemFactory)
    destruction_list_review = factory.SubFactory(DestructionListReviewFactory)
    text = factory.Faker("text")
    suggestion = factory.fuzzy.FuzzyChoice(choices=Suggestion.values)

    class Meta:
        model = "destruction.DestructionListItemReview"


class DestructionListAssigneeFactory(factory.django.DjangoModelFactory):
    destruction_list = factory.SubFactory(DestructionListFactory)
    assignee = factory.SubFactory(UserFactory)
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = "destruction.DestructionListAssignee"
