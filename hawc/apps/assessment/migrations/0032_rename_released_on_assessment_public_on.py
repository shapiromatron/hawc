# Generated by Django 3.2.11 on 2022-01-24 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0031_assessment_released_on'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assessment',
            old_name='released_on',
            new_name='public_on',
        ),
    ]
