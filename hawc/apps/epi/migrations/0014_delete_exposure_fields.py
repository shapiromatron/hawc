# Generated by Django 1.11.15 on 2019-04-02 00:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("epi", "0013_move_central_tendency"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="exposure",
            name="estimate",
        ),
        migrations.RemoveField(
            model_name="exposure",
            name="estimate_type",
        ),
        migrations.RemoveField(
            model_name="exposure",
            name="lower_ci",
        ),
        migrations.RemoveField(
            model_name="exposure",
            name="lower_range",
        ),
        migrations.RemoveField(
            model_name="exposure",
            name="upper_ci",
        ),
        migrations.RemoveField(
            model_name="exposure",
            name="upper_range",
        ),
        migrations.RemoveField(
            model_name="exposure",
            name="variance",
        ),
        migrations.RemoveField(
            model_name="exposure",
            name="variance_type",
        ),
    ]
