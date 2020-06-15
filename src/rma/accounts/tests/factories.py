import factory


class RoleFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")

    class Meta:
        model = "accounts.Role"


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user-{n}")
    email = factory.Sequence(lambda n: f"user-{n}@rma")
    role = factory.SubFactory(RoleFactory)

    class Meta:
        model = "accounts.User"
