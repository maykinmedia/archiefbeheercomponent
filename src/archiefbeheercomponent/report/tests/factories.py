import factory

from archiefbeheercomponent.report.utils import convert_to_pdf


class DestructionReportFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("bs")
    content_pdf = factory.django.FileField(
        data=convert_to_pdf("<h1>A test report</h1>"), filename="report.pdf"
    )
    content_csv = factory.django.FileField(
        data="Column1,Column2,\r\n", filename="report.csv"
    )

    class Meta:
        model = "report.DestructionReport"
