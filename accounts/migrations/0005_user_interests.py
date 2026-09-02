from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0004_alter_user_avatar")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="interests",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
