from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rhymes", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="rhyme",
            index=models.Index(fields=["is_published", "category"], name="rhymes_rhyme_pub_categ_idx"),
        ),
        migrations.AddIndex(
            model_name="rhyme",
            index=models.Index(fields=["difficulty", "is_published"], name="rhymes_rhyme_diff_pub_idx"),
        ),
    ]
