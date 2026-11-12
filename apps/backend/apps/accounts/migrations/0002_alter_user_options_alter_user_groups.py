# Generated to align the custom user model with Django 5.2's PermissionsMixin defaults.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name": "user"},
        ),
        migrations.AlterField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to.",
                related_name="accounts_user_set",
                related_query_name="accounts_user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
    ]
