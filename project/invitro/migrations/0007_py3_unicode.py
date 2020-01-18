# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-02 20:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invitro", "0006_auto_20160114_1524"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ivcelltype",
            name="culture_type",
            field=models.CharField(
                choices=[
                    ("nr", "not reported"),
                    ("im", "Immortalized cell line"),
                    ("pc", "Primary culture"),
                    ("tt", "Transient transfected cell line"),
                    ("st", "Stably transfected cell line"),
                    ("ts", "Transient transfected into stably transfected cell line"),
                    ("na", "not applicable"),
                ],
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="ivcelltype",
            name="sex",
            field=models.CharField(
                choices=[
                    ("m", "Male"),
                    ("f", "Female"),
                    ("mf", "Male and female"),
                    ("na", "Not-applicable"),
                    ("nr", "Not-reported"),
                ],
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="ivcelltype",
            name="source",
            field=models.CharField(max_length=128, verbose_name="Source of cell cultures"),
        ),
        migrations.AlterField(
            model_name="ivcelltype",
            name="strain",
            field=models.CharField(default="not applicable", max_length=64),
        ),
        migrations.AlterField(
            model_name="ivchemical",
            name="cas",
            field=models.CharField(
                blank=True, max_length=40, verbose_name="Chemical identifier (CAS)"
            ),
        ),
        migrations.AlterField(
            model_name="ivchemical",
            name="cas_inferred",
            field=models.BooleanField(
                default=False,
                help_text="Was the correct CAS inferred or incorrect in the original document?",
                verbose_name="CAS inferred?",
            ),
        ),
        migrations.AlterField(
            model_name="ivchemical",
            name="cas_notes",
            field=models.CharField(max_length=256, verbose_name="CAS determination notes"),
        ),
        migrations.AlterField(
            model_name="ivchemical",
            name="dilution_storage_notes",
            field=models.TextField(
                help_text="Dilution, storage, and observations such as precipitation should be noted here."
            ),
        ),
        migrations.AlterField(
            model_name="ivchemical",
            name="purity",
            field=models.CharField(
                help_text="Ex: >99%, not-reported, etc.",
                max_length=32,
                verbose_name="Chemical purity",
            ),
        ),
        migrations.AlterField(
            model_name="ivchemical",
            name="purity_confirmed",
            field=models.BooleanField(
                default=False, verbose_name="Purity experimentally confirmed"
            ),
        ),
        migrations.AlterField(
            model_name="ivchemical",
            name="source",
            field=models.CharField(max_length=128, verbose_name="Source of chemical"),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="LOEL",
            field=models.SmallIntegerField(
                default=-999, help_text="Lowest observed effect level", verbose_name="LOEL",
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="NOEL",
            field=models.SmallIntegerField(
                default=-999, help_text="No observed effect level", verbose_name="NOEL"
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint", name="additional_fields", field=models.TextField(default="{}"),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="data_location",
            field=models.CharField(
                blank=True,
                help_text="Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="data_type",
            field=models.CharField(
                choices=[("C", "Continuous"), ("D", "Dichotomous"), ("NR", "Not reported")],
                default="C",
                max_length=2,
                verbose_name="Dataset type",
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="effect",
            field=models.CharField(help_text="Effect, using common-vocabulary", max_length=128),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="endpoint_notes",
            field=models.TextField(
                blank=True, help_text="Any additional notes regarding the endpoint itself",
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="monotonicity",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "N/A, single dose level study"),
                    (1, "N/A, no effects detected"),
                    (2, "yes, visual appearance of monotonicity but no trend"),
                    (3, "yes, monotonic and significant trend"),
                    (4, "yes, visual appearance of non-monotonic but no trend"),
                    (5, "yes, non-monotonic and significant trend"),
                    (6, "no pattern"),
                    (7, "unclear"),
                    (8, "not-reported"),
                ],
                default=8,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="observation_time_units",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "not-reported"),
                    (1, "seconds"),
                    (2, "minutes"),
                    (3, "hours"),
                    (4, "days"),
                    (5, "weeks"),
                    (6, "months"),
                ],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="overall_pattern",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "not-available"),
                    (1, "increase"),
                    (2, "increase, then decrease"),
                    (6, "increase, then no change"),
                    (3, "decrease"),
                    (4, "decrease, then increase"),
                    (7, "decrease, then no change"),
                    (5, "no clear pattern"),
                    (8, "no change"),
                ],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="response_units",
            field=models.CharField(blank=True, max_length=64, verbose_name="Response units"),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="result_notes",
            field=models.TextField(blank=True, help_text="Qualitative description of the results"),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="short_description",
            field=models.CharField(
                help_text="Short (<128 character) description of effect & measurement",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="statistical_test_notes",
            field=models.CharField(
                blank=True,
                help_text="Notes describing details on the statistical tests performed",
                max_length=256,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="trend_test",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "not reported"),
                    (1, "not analyzed"),
                    (2, "not applicable"),
                    (3, "significant"),
                    (4, "not significant"),
                ],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="trend_test_notes",
            field=models.CharField(
                blank=True,
                help_text="Notes describing details on the trend-test performed",
                max_length=256,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="values_estimated",
            field=models.BooleanField(
                default=False,
                help_text="Response values were estimated using a digital ruler or other methods",
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="variance_type",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "NA"), (1, "SD"), (2, "SE")], default=0
            ),
        ),
        migrations.AlterField(
            model_name="ivendpointgroup",
            name="cytotoxicity_observed",
            field=models.NullBooleanField(
                choices=[(None, "not reported"), (False, "not observed"), (True, "observed")],
                default=None,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpointgroup",
            name="difference_control",
            field=models.CharField(
                choices=[
                    ("nc", "no-change"),
                    ("-", "decrease"),
                    ("+", "increase"),
                    ("nt", "not-tested"),
                ],
                default="nc",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpointgroup",
            name="precipitation_observed",
            field=models.NullBooleanField(
                choices=[(None, "not reported"), (False, "not observed"), (True, "observed")],
                default=None,
            ),
        ),
        migrations.AlterField(
            model_name="ivendpointgroup",
            name="significant_control",
            field=models.CharField(
                choices=[
                    ("nr", "not reported"),
                    ("si", "p ≤ 0.05"),
                    ("ns", "not significant"),
                    ("na", "not applicable"),
                ],
                default="nr",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="ivexperiment",
            name="cell_notes",
            field=models.TextField(
                blank=True,
                help_text="Description of type of cell-line used (ex: primary cell-line, immortalized cell-line, stably transfected cell-line, transient transfected cell-line, etc.)",
            ),
        ),
        migrations.AlterField(
            model_name="ivexperiment",
            name="control_notes",
            field=models.CharField(
                blank=True, help_text="Additional details related to controls", max_length=256,
            ),
        ),
        migrations.AlterField(
            model_name="ivexperiment",
            name="dosing_notes",
            field=models.TextField(
                blank=True,
                help_text="Notes describing dosing-protocol, including duration-details",
            ),
        ),
        migrations.AlterField(
            model_name="ivexperiment",
            name="metabolic_activation",
            field=models.CharField(
                choices=[
                    ("+", "with metabolic activation"),
                    ("-", "without metabolic activation"),
                    ("na", "not applicable"),
                    ("nr", "not reported"),
                ],
                default="nr",
                help_text="Was metabolic-activation used in system (ex: S9)?",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="ivexperiment",
            name="negative_control",
            field=models.CharField(
                blank=True, help_text="Negative control chemical or other notes", max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="ivexperiment",
            name="positive_control",
            field=models.CharField(
                blank=True, help_text="Positive control chemical or other notes", max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="ivexperiment",
            name="serum",
            field=models.CharField(
                help_text="Percent serum, serum-type, and/or description", max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="ivexperiment",
            name="transfection",
            field=models.CharField(
                help_text='Details on transfection methodology and details on genes or other genetic material introduced into assay, or "not-applicable"',
                max_length=256,
            ),
        ),
        migrations.AlterField(
            model_name="ivexperiment",
            name="vehicle_control",
            field=models.CharField(
                blank=True, help_text="Vehicle control chemical or other notes", max_length=128,
            ),
        ),
    ]
