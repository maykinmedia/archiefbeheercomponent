import factory


class DestructionReportFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("bs")
    content = factory.django.FileField(
        data=b"<h1>A test report</h1>", filename="report.html"
    )

    class Meta:
        model = "report.DestructionReport"
