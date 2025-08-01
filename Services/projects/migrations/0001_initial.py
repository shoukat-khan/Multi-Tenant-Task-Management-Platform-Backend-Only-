# Generated by Django 4.2.23 on 2025-07-19 20:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("teams", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="Name of the project", max_length=200),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, help_text="Description of the project", null=True
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("planning", "Planning"),
                            ("active", "Active"),
                            ("on_hold", "On Hold"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="planning",
                        help_text="Current status of the project",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("urgent", "Urgent"),
                        ],
                        default="medium",
                        help_text="Priority level of the project",
                        max_length=20,
                    ),
                ),
                (
                    "start_date",
                    models.DateField(
                        blank=True, help_text="Project start date", null=True
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        blank=True, help_text="Project end date", null=True
                    ),
                ),
                (
                    "completed_date",
                    models.DateField(
                        blank=True,
                        help_text="Date when project was completed",
                        null=True,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, help_text="Whether the project is active"
                    ),
                ),
                (
                    "budget",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Project budget",
                        max_digits=12,
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        help_text="User who created the project",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "manager",
                    models.ForeignKey(
                        help_text="Project manager",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="managed_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        help_text="Team responsible for the project",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projects",
                        to="teams.team",
                    ),
                ),
            ],
            options={
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
                "db_table": "projects",
                "ordering": ["-created_at"],
            },
        ),
    ]
