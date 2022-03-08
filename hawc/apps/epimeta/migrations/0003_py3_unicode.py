# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-02 20:00
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epimeta", "0002_auto_20151207_1447"),
    ]

    operations = [
        migrations.AlterField(
            model_name="metaprotocol",
            name="lit_search_end_date",
            field=models.DateField(
                blank=True, null=True, verbose_name="Literature search end-date"
            ),
        ),
        migrations.AlterField(
            model_name="metaprotocol",
            name="lit_search_notes",
            field=models.TextField(blank=True, verbose_name="Literature search notes"),
        ),
        migrations.AlterField(
            model_name="metaprotocol",
            name="lit_search_start_date",
            field=models.DateField(
                blank=True, null=True, verbose_name="Literature search start-date"
            ),
        ),
        migrations.AlterField(
            model_name="metaprotocol",
            name="lit_search_strategy",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "Systematic"), (1, "Other")],
                default=0,
                verbose_name="Literature search strategy",
            ),
        ),
        migrations.AlterField(
            model_name="metaprotocol",
            name="name",
            field=models.CharField(max_length=128, verbose_name="Protocol name"),
        ),
        migrations.AlterField(
            model_name="metaprotocol",
            name="protocol_type",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "Meta-analysis"), (1, "Pooled-analysis")], default=0
            ),
        ),
        migrations.AlterField(
            model_name="metaprotocol",
            name="total_references",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="References identified through initial literature-search before application of inclusion/exclusion criteria",
                null=True,
                verbose_name="Total number of references found",
            ),
        ),
        migrations.AlterField(
            model_name="metaprotocol",
            name="total_studies_identified",
            field=models.PositiveIntegerField(
                help_text="Total references identified for inclusion after application of literature review and screening criteria",
                verbose_name="Total number of studies identified",
            ),
        ),
        migrations.AlterField(
            model_name="metaresult",
            name="adjustment_factors",
            field=models.ManyToManyField(
                blank=True,
                help_text="All factors which were included in final model",
                related_name="meta_adjustments",
                to="epi.AdjustmentFactor",
            ),
        ),
        migrations.AlterField(
            model_name="metaresult",
            name="ci_units",
            field=models.FloatField(
                blank=True,
                default=0.95,
                help_text="A 95% CI is written as 0.95.",
                null=True,
                verbose_name="Confidence Interval (CI)",
            ),
        ),
        migrations.AlterField(
            model_name="metaresult",
            name="data_location",
            field=models.CharField(
                blank=True,
                help_text="Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="metaresult",
            name="lower_ci",
            field=models.FloatField(
                help_text="Numerical value for lower-confidence interval",
                verbose_name="Lower CI",
            ),
        ),
        migrations.AlterField(
            model_name="metaresult",
            name="n",
            field=models.PositiveIntegerField(
                help_text="Number of individuals included from all analyses"
            ),
        ),
        migrations.AlterField(
            model_name="metaresult",
            name="upper_ci",
            field=models.FloatField(
                help_text="Numerical value for upper-confidence interval",
                verbose_name="Upper CI",
            ),
        ),
        migrations.AlterField(
            model_name="singleresult",
            name="ci_units",
            field=models.FloatField(
                blank=True,
                default=0.95,
                help_text="A 95% CI is written as 0.95.",
                null=True,
                verbose_name="Confidence Interval (CI)",
            ),
        ),
        migrations.AlterField(
            model_name="singleresult",
            name="estimate",
            field=models.FloatField(
                blank=True,
                help_text="Enter the numerical risk-estimate presented for this result",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="singleresult",
            name="exposure_name",
            field=models.CharField(
                help_text='Enter a descriptive-name for the single study result (e.g., "Smith et al. 2000, obese-males")',
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="singleresult",
            name="lower_ci",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for lower-confidence interval",
                null=True,
                verbose_name="Lower CI",
            ),
        ),
        migrations.AlterField(
            model_name="singleresult",
            name="n",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Enter the number of observations for this result",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="singleresult",
            name="upper_ci",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for upper-confidence interval",
                null=True,
                verbose_name="Upper CI",
            ),
        ),
        migrations.AlterField(
            model_name="singleresult",
            name="weight",
            field=models.FloatField(
                blank=True,
                help_text="For meta-analysis, enter the fraction-weight assigned for each result (leave-blank for pooled analyses)",
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(1),
                ],
            ),
        ),
    ]
