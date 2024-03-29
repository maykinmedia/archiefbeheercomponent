# Generated by Django 2.2.26 on 2022-02-01 11:17

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ("theme", "0002_auto_20210224_1437"),
    ]

    operations = [
        migrations.AlterField(
            model_name="themeconfig",
            name="color_link_dark",
            field=models.CharField(
                default="051f31",
                help_text="Typically a darker shade of the link color, used for hover states.",
                max_length=6,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[0-9a-fA-F]+"),
                        "Enter a valid HTML color code value consisting of only hexidecimal characters.",
                        "invalid",
                    )
                ],
                verbose_name="Link color (dark)",
            ),
        ),
    ]
