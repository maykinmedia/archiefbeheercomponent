# Generated by Django 2.2.24 on 2021-11-30 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emails", "0007_auto_20210415_1029"),
    ]

    operations = [
        migrations.AlterField(
            model_name="automaticemail",
            name="type",
            field=models.CharField(
                choices=[
                    ("report_available", "Report available"),
                    ("review_required", "Review required"),
                    ("changes_required", "Changes required"),
                    ("review_reminder", "Review reminder"),
                ],
                help_text="The type of email",
                max_length=200,
                unique=True,
                verbose_name="type",
            ),
        ),
    ]
