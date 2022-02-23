# Generated by Django 3.2.11 on 2022-02-23 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epiv2", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="dataextraction",
            old_name="measurement_timing",
            new_name="outcome_measurement_timing",
        ),
        migrations.RenameField(model_name="exposurelevel", old_name="minimum", new_name="lower",),
        migrations.RenameField(model_name="exposurelevel", old_name="maximum", new_name="upper",),
        migrations.RenameField(model_name="outcome", old_name="name", new_name="endpoint",),
        migrations.RemoveField(model_name="exposurelevel", name="central_tendency",),
        migrations.RemoveField(model_name="exposurelevel", name="central_tendency_type",),
        migrations.AddField(
            model_name="exposurelevel", name="mean", field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="exposurelevel",
            name="median",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="exposurelevel",
            name="ultype",
            field=models.CharField(
                blank=True,
                choices=[("MX", "Min/Max"), ("N5", "5/95"), ("N9", "1/99")],
                default="MX",
                max_length=128,
                verbose_name="Upper/lower type",
            ),
        ),
        migrations.AddField(
            model_name="exposurelevel",
            name="units",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="outcome", name="comments", field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="adjustmentfactor",
            name="description",
            field=models.CharField(blank=True, help_text="Comma separated list", max_length=128),
        ),
        migrations.AlterField(
            model_name="dataextraction",
            name="statistical_method",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="dataextraction",
            name="sub_population",
            field=models.CharField(
                help_text="Use N/A if sub population is not relevant", max_length=64
            ),
        ),
    ]
