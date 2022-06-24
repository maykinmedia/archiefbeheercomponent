# Generated by Django 2.2.12 on 2020-06-05 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the role",
                        max_length=255,
                        unique=True,
                        verbose_name="name",
                    ),
                ),
                (
                    "organisatie_onderdeel",
                    models.URLField(blank=True, verbose_name="organisatie onderdeel"),
                ),
                (
                    "can_start_destruction",
                    models.BooleanField(
                        default=False,
                        help_text='Designates whether people in this role can create a "vernietigingslijst", which is the starting point for the "records destruction" process.',
                        verbose_name="can start destruction",
                    ),
                ),
                (
                    "can_review_destruction",
                    models.BooleanField(
                        default=False,
                        help_text="Designates if people in this role can review created record destruction lists and approve/reject them.",
                        verbose_name="can review destruction",
                    ),
                ),
                (
                    "can_view_case_details",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether people in this role can view the contents of zaken listed on the record destruction lists.",
                        verbose_name="can view case details",
                    ),
                ),
            ],
            options={
                "verbose_name": "role",
                "verbose_name_plural": "roles",
            },
        ),
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="accounts.Role",
                verbose_name="role",
            ),
        ),
    ]
