import factory


class RoleFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"role-{n}")

    class Meta:
        model = "accounts.Role"

    class Params:
        record_manager = factory.Trait(
            can_start_destruction=True, can_view_case_details=True,
        )
        process_owner = factory.Trait(
            can_review_destruction=True, can_view_case_details=True,
        )
        archivaris = factory.Trait(can_review_destruction=True,)


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user-{n}")
    email = factory.Sequence(lambda n: f"user-{n}@archiefbeheercomponent")
    role = factory.SubFactory(RoleFactory)

    class Meta:
        model = "accounts.User"
