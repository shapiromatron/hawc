# Generated by Django 3.1.3 on 2021-01-11 03:35

from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0014_add_topic_model"),
    ]

    operations = [UnaccentExtension()]
