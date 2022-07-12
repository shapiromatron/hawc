# Generated by Django 3.2.14 on 2022-07-12 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epiv2', '0003_auto_20220708_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adjustmentfactor',
            name='description',
            field=models.CharField(help_text='Enter the list of covariates in the model, separated by commas. These can be brief and ideally entered uniformly across studies when possible. Additional detail can be added in the comments or in study evaluation (e.g., enter "smoking" for consistency instead of "pack-years")', max_length=512),
        ),
    ]
