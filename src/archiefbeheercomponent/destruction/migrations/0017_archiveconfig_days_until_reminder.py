# Generated by Django 2.2.20 on 2021-11-12 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("destruction", "0016_auto_20210413_1049"),
    ]

    operations = [
        migrations.AddField(
            model_name="archiveconfig",
            name="days_until_reminder",
            field=models.PositiveIntegerField(
                default=7,
                help_text="Number of days until an email is sent reminding that the list needs to be dealt with",
                verbose_name="days until reminder",
            ),
        ),
    ]
