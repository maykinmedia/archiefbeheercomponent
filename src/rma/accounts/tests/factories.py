import factory


class RoleFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"role-{n}")

    class Meta:
        model = "accounts.Role"


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user-{n}")
    email = factory.Sequence(lambda n: f"user-{n}@rma")
    role = factory.SubFactory(RoleFactory)

    class Meta:
        model = "accounts.User"
