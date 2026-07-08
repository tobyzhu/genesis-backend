# Generated manually for vip_crm agent profile support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assistant", "0001_initial_history"),
    ]

    operations = [
        migrations.AddField(
            model_name="assistantthread",
            name="profile_id",
            field=models.CharField(default="general", max_length=32),
        ),
    ]
