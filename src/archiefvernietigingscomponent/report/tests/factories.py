import factory


class DestructionReportFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("bs")
    content = factory.django.FileField(data=b"A test report", filename="report.txt")

    class Meta:
        model = "report.DestructionReport"
