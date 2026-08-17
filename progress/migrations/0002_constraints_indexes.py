from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("progress", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="badge",
            name="name",
            field=models.CharField(max_length=80, unique=True),
        ),
        migrations.AddConstraint(
            model_name="rhymeprogress",
            constraint=models.UniqueConstraint(fields=("user", "rhyme"), name="unique_user_rhyme_progress"),
        ),
        migrations.AddConstraint(
            model_name="userbadge",
            constraint=models.UniqueConstraint(fields=("user", "badge"), name="unique_user_badge"),
        ),
        migrations.AddIndex(
            model_name="rhymeprogress",
            index=models.Index(fields=["user", "completed"], name="progress_rhyme_user_comp_idx"),
        ),
        migrations.AddIndex(
            model_name="rhymeprogress",
            index=models.Index(fields=["user", "last_played"], name="progress_rhyme_user_last_idx"),
        ),
    ]
