# Generated by Django 5.0.8 on 2024-08-26 13:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0039_tag_taggeditem"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tag",
            name="assessment",
        ),
        migrations.RemoveField(
            model_name="tag",
            name="text_color",
        ),
    ]
