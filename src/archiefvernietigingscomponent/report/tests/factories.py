import factory

from archiefvernietigingscomponent.report.utils import convert_to_pdf


class DestructionReportFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("bs")
    content = factory.django.FileField(
        data=convert_to_pdf("<h1>A test report</h1>"), filename="report.pdf"
    )

    class Meta:
        model = "report.DestructionReport"
