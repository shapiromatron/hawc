# Generated by Django 3.2.12 on 2022-02-23 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epiv2', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='design',
            name='comments',
            field=models.TextField(blank=True),
        ),
    ]
