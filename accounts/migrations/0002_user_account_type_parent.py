from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="account_type",
            field=models.CharField(
                choices=[("learner", "Learner"), ("parent", "Parent / Guardian")],
                default="learner",
                max_length=12,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"account_type": "parent"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="age_group",
            field=models.CharField(
                blank=True,
                choices=[
                    ("2-4", "2 – 4 years"),
                    ("4-6", "4 – 6 years"),
                    ("6-8", "6 – 8 years"),
                ],
                default="4-6",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="parent_email",
            field=models.EmailField(
                blank=True,
                help_text="Parent/guardian email for learner updates.",
                max_length=254,
            ),
        ),
    ]
