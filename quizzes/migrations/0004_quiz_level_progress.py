from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quizzes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuizLevelProgress",
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
                    "level",
                    models.PositiveIntegerField(),
                ),
                (
                    "difficulty",
                    models.CharField(max_length=20),
                ),
                (
                    "completed",
                    models.BooleanField(default=False),
                ),
                (
                    "attempts",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "best_score",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "best_percentage",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "stars",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "last_score",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "last_percentage",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="quiz_level_progress",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("user", "level"),
                        name="unique_user_quiz_level_progress",
                    ),
                ],
                "indexes": [
                    models.Index(
                        fields=("user", "completed"),
                        name="quiz_level_user_completed_idx",
                    ),
                ],
            },
        ),
    ]