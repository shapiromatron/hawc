from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myuser", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hawcuser",
            name="groups",
            field=models.ManyToManyField(
                related_query_name="user",
                related_name="user_set",
                to="auth.Group",
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                verbose_name="groups",
            ),
        ),
        migrations.AlterField(
            model_name="hawcuser",
            name="last_login",
            field=models.DateTimeField(null=True, verbose_name="last login", blank=True),
        ),
    ]
