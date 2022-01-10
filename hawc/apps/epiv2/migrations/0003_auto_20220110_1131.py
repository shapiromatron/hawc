# Generated by Django 3.2.10 on 2022-01-10 17:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('epiv2', '0002_auto_20220107_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='adjustmentfactor',
            name='name',
            field=models.CharField(default='Adjustment factor <built-in function id>', help_text='A unique name for this adjustment factor that will help you identify it later.', max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exposure',
            name='name',
            field=models.CharField(default='Exposure <built-in function id>', help_text='A unique name for this exposure that will help you identify it later.', max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exposurelevel',
            name='name',
            field=models.CharField(default='Exposure level <built-in function id>', help_text='A unique name for this exposure level that will help you identify it later.', max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='outcome',
            name='name',
            field=models.CharField(default='Outcome <built-in function id>', help_text='A unique name for this health outcome that will help you identify it later.', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='adjustmentfactor',
            name='description',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='adjustment_factor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='epiv2.adjustmentfactor'),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='ci_lcl',
            field=models.FloatField(blank=True, null=True, verbose_name='Confidence Interval LCL'),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='ci_ucl',
            field=models.FloatField(blank=True, null=True, verbose_name='Confidence Interval UCL'),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='comments',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='confidence',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Study confidence'),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='data_location',
            field=models.CharField(blank=True, help_text='e.g., table number', max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='effect_description',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='effect_estimate',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='effect_estimate_type',
            field=models.CharField(blank=True, choices=[('OT', 'Other')], max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='exposure_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='epiv2.exposurelevel'),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='exposure_rank',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Rank this comparison group by exposure (lowest exposure group = 1)', null=True),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='measurement_timing',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='n',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='outcome',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='epiv2.outcome'),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='pvalue',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='p-value'),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='sd_or_se',
            field=models.FloatField(blank=True, null=True, verbose_name='Standard Deviation or Standard Error'),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='significant',
            field=models.BooleanField(blank=True, choices=[(True, 'Yes'), (False, 'No'), (None, 'N/A')], null=True, verbose_name='Statistically Significant'),
        ),
        migrations.AlterField(
            model_name='dataextraction',
            name='statistical_method',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='exposure',
            name='analytic_method',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='exposure',
            name='comments',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='exposure',
            name='exposure_route',
            field=models.CharField(blank=True, choices=[('IH', 'Inhalation'), ('OR', 'Oral'), ('DE', 'Dermal'), ('IU', 'In utero'), ('IV', 'Intravenous'), ('UK', 'Unknown/Total')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='exposure',
            name='measurement_timing',
            field=models.CharField(blank=True, help_text='If timing is based on something other than age, specify the timing (e.g., start of employment at Factory A). If cross-sectional, enter "cross-sectional"', max_length=128, null=True, verbose_name='Timing of exposure measurement'),
        ),
        migrations.AlterField(
            model_name='exposure',
            name='measurement_type',
            field=models.ManyToManyField(blank=True, to='epiv2.MeasurementType', verbose_name='Exposure measurement type'),
        ),
        migrations.AlterField(
            model_name='exposurelevel',
            name='central_tendency_type',
            field=models.CharField(blank=True, choices=[('MED', 'Median')], default='MED', max_length=128, null=True, verbose_name='Central tendency type (median preferred)'),
        ),
        migrations.AlterField(
            model_name='exposurelevel',
            name='comments',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Exposure level comments'),
        ),
        migrations.AlterField(
            model_name='exposurelevel',
            name='data_location',
            field=models.CharField(blank=True, help_text='e.g., table number', max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='exposurelevel',
            name='exposure_measurement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='epiv2.exposure'),
        ),
        migrations.AlterField(
            model_name='exposurelevel',
            name='maximum',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='exposurelevel',
            name='minimum',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='exposurelevel',
            name='neg_exposure',
            field=models.FloatField(blank=True, help_text='e.g., %% below the LOD', null=True, verbose_name='Percent with negligible exposure'),
        ),
        migrations.AlterField(
            model_name='exposurelevel',
            name='percentile25',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='exposurelevel',
            name='percentile75',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='exposurelevel',
            name='sub_population',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Sub-population (if relevant)'),
        ),
        migrations.AlterField(
            model_name='outcome',
            name='health_outcome_system',
            field=models.CharField(blank=True, choices=[('RE', 'Reproductive')], help_text='If multiple cancer types are present, report all types under Cancer.', max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='studypopulation',
            name='region',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Other geographic information'),
        ),
        migrations.AlterField(
            model_name='studypopulation',
            name='source',
            field=models.CharField(blank=True, choices=[('GP', 'General population'), ('OC', 'Occupational'), ('OT', 'Other')], max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='studypopulation',
            name='study_design',
            field=models.CharField(blank=True, choices=[('CO', 'Cohort'), ('CC', 'Case-control'), ('NC', 'Nested case-control'), ('CR', 'Case report'), ('SE', 'Case series'), ('RT', 'Randomized controlled trial'), ('NT', 'Non-randomized controlled trial'), ('CS', 'Cross-sectional'), ('OT', 'Other')], max_length=128, null=True),
        ),
    ]
