# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0001_initial'),
        ('study', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aggregation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('aggregation_type', models.CharField(default=b'E', help_text=b'The purpose for creating this aggregation.', max_length=2, choices=[(b'E', b'Evidence'), (b'M', b'Mode-of-action'), (b'CD', b'Candidate Reference Values')])),
                ('summary_text', models.TextField(default=b'')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnimalGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('sex', models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'B', b'Both')])),
                ('dose_groups', models.PositiveSmallIntegerField(default=4, verbose_name=b'Number of Dose Groups', validators=[django.core.validators.MinValueValidator(1)])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DoseGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dose_group_id', models.PositiveSmallIntegerField()),
                ('dose', models.DecimalField(max_digits=50, decimal_places=25, validators=[django.core.validators.MinValueValidator(0)])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DoseUnits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('units', models.CharField(unique=True, max_length=20)),
                ('administered', models.BooleanField(default=False)),
                ('converted', models.BooleanField(default=False)),
                ('hed', models.BooleanField(default=False, verbose_name=b'Human Equivalent Dose')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'dose units',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DosingRegime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('route_of_exposure', models.CharField(max_length=2, choices=[(b'OD', 'Oral Diet'), (b'OG', 'Oral Gavage'), (b'OW', 'Oral Drinking Water'), (b'I', 'Inhalation'), (b'D', 'Dermal'), (b'SI', 'Subcutaneous Injection'), (b'IO', 'in ovo'), (b'O', 'Other')])),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Endpoint',
            fields=[
                ('baseendpoint_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='assessment.BaseEndpoint')),
                ('system', models.CharField(max_length=128, blank=True)),
                ('organ', models.CharField(max_length=128, blank=True)),
                ('effect', models.CharField(max_length=128, blank=True)),
                ('data_location', models.CharField(help_text=b'Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)', max_length=128, blank=True)),
                ('response_units', models.CharField(max_length=15, verbose_name=b'Response units')),
                ('data_type', models.CharField(default=b'D', max_length=2, verbose_name=b'Dataset type', choices=[(b'C', b'Continuous'), (b'D', b'Dichotomous'), (b'DC', b'Dichotomous Cancer')])),
                ('variance_type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'NA'), (1, b'SD'), (2, b'SE')])),
                ('NOAEL', models.SmallIntegerField(default=-999, verbose_name=b'NOAEL')),
                ('LOAEL', models.SmallIntegerField(default=-999, verbose_name=b'LOAEL')),
                ('FEL', models.SmallIntegerField(default=-999, verbose_name=b'FEL')),
                ('data_reported', models.BooleanField(default=True, help_text=b'Dose-response data for endpoint are available in the literature source')),
                ('data_extracted', models.BooleanField(default=True, help_text=b'Dose-response data for endpoint are extracted from literature into HAWC')),
                ('values_estimated', models.BooleanField(default=False, help_text=b'Response values were estimated using a digital ruler or other methods')),
                ('individual_animal_data', models.BooleanField(default=False, help_text=b'If individual response data are available for each animal.')),
                ('monotonicity', models.PositiveSmallIntegerField(choices=[(0, b'N/A, single dose level study'), (1, b'N/A, no effects detected'), (2, b'yes, visual appearance of monotonicity but no trend'), (3, b'yes, monotonic and significant trend'), (4, b'yes, visual appearance of non-monotonic but no trend'), (5, b'yes, non-monotonic and significant trend'), (6, b'no pattern'), (7, b'unclear')])),
                ('statistical_test', models.CharField(max_length=256, blank=True)),
                ('trend_value', models.FloatField(null=True, blank=True)),
                ('results_notes', models.TextField(help_text=b'Qualitative description of the results', blank=True)),
                ('endpoint_notes', models.TextField(help_text=b'Any additional notes related to this endpoint itself, not related to results', blank=True)),
                ('additional_fields', models.TextField(default=b'{}')),
            ],
            options={
            },
            bases=('assessment.baseendpoint',),
        ),
        migrations.CreateModel(
            name='EndpointGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dose_group_id', models.IntegerField()),
                ('n', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('incidence', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('response', models.DecimalField(null=True, max_digits=50, decimal_places=25, blank=True)),
                ('variance', models.DecimalField(blank=True, null=True, max_digits=50, decimal_places=25, validators=[django.core.validators.MinValueValidator(0)])),
                ('significant', models.BooleanField(default=False, verbose_name=b'Statistically significant from control')),
                ('significance_level', models.FloatField(default=0, verbose_name=b'Statistical significance level', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('endpoint', models.ForeignKey(related_name=b'endpoint_group', to='animal.Endpoint')),
            ],
            options={
                'ordering': ('endpoint', 'dose_group_id'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('type', models.CharField(max_length=2, choices=[(b'Ac', b'Acute'), (b'Sb', b'Subchronic'), (b'Ch', b'Chronic'), (b'Ca', b'Cancer'), (b'Me', b'Mechanistic'), (b'Rp', b'Reproductive'), (b'Dv', b'Developmental'), (b'Ot', b'Other')])),
                ('cas', models.CharField(max_length=40, verbose_name=b'Chemical identifier (CAS)', blank=True)),
                ('purity_available', models.BooleanField(default=True, verbose_name=b'Chemical purity available?')),
                ('purity', models.FloatField(blank=True, null=True, verbose_name=b'Chemical purity (%)', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('study', models.ForeignKey(related_name=b'experiments', to='study.Study')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GenerationalAnimalGroup',
            fields=[
                ('animalgroup_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='animal.AnimalGroup')),
                ('generation', models.CharField(max_length=2, choices=[(b'F0', b'Parent-Generation (F0)'), (b'F1', b'First-Generation (F1)'), (b'F2', b'Second-Generation (F2)')])),
                ('parents', models.ManyToManyField(related_name=b'parents+', null=True, to=b'animal.GenerationalAnimalGroup', blank=True)),
            ],
            options={
            },
            bases=('animal.animalgroup',),
        ),
        migrations.CreateModel(
            name='IndividualAnimal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('response', models.DecimalField(max_digits=50, decimal_places=25)),
                ('endpoint_group', models.ForeignKey(related_name=b'individual_data', to='animal.EndpointGroup')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReferenceValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('point_of_departure', models.DecimalField(max_digits=50, decimal_places=25, validators=[django.core.validators.MinValueValidator(0)])),
                ('type', models.PositiveSmallIntegerField(default=1, choices=[(1, b'Oral RfD'), (2, b'Inhalation RfD'), (3, b'Oral CSF'), (4, b'Inhalation CSF')])),
                ('justification', models.TextField()),
                ('aggregate_uf', models.DecimalField(max_digits=10, decimal_places=3, blank=True)),
                ('reference_value', models.DecimalField(max_digits=50, decimal_places=25, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('aggregation', models.ForeignKey(help_text=b'Specify a collection of endpoints which justify this reference-value', to='animal.Aggregation')),
                ('assessment', models.ForeignKey(related_name=b'reference_values', to='assessment.Assessment')),
                ('units', models.ForeignKey(related_name=b'units+', to='animal.DoseUnits')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Enter species in singular (ex: Mouse, not Mice)', unique=True, max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'species',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Strain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('species', models.ForeignKey(to='animal.Species')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UncertaintyFactorEndpoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uf_type', models.CharField(max_length=3, verbose_name=b'Uncertainty Value Type', choices=[(b'UFA', b'Interspecies uncertainty'), (b'UFH', b'Intraspecies variability'), (b'UFS', b'Subchronic to chronic extrapolation'), (b'UFL', b'Use of a LOAEL in absence of a NOAEL'), (b'UFD', b'Database incomplete'), (b'UFO', b'Other')])),
                ('value', models.DecimalField(default=10, help_text=b'Note that 3*3=10 for all uncertainty value calculations; therefore specifying 3.33 is not required.', max_digits=5, decimal_places=3, validators=[django.core.validators.MinValueValidator(1)])),
                ('description', models.TextField(verbose_name=b'Justification', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('endpoint', models.ForeignKey(related_name=b'ufs', to='animal.Endpoint')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UncertaintyFactorRefVal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uf_type', models.CharField(max_length=3, verbose_name=b'Uncertainty Value Type', choices=[(b'UFA', b'Interspecies uncertainty'), (b'UFH', b'Intraspecies variability'), (b'UFS', b'Subchronic to chronic extrapolation'), (b'UFL', b'Use of a LOAEL in absence of a NOAEL'), (b'UFD', b'Database incomplete'), (b'UFO', b'Other')])),
                ('value', models.DecimalField(default=10, help_text=b'Note that 3*3=10 for all uncertainty value calculations; therefore specifying 3.33 is not required.', max_digits=5, decimal_places=3, validators=[django.core.validators.MinValueValidator(1)])),
                ('description', models.TextField(verbose_name=b'Justification', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('reference_value', models.ForeignKey(related_name=b'ufs', to='animal.ReferenceValue')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='uncertaintyfactorrefval',
            unique_together=set([('reference_value', 'uf_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='uncertaintyfactorendpoint',
            unique_together=set([('endpoint', 'uf_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='strain',
            unique_together=set([('species', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='referencevalue',
            unique_together=set([('assessment', 'type', 'units')]),
        ),
        migrations.AddField(
            model_name='endpoint',
            name='animal_group',
            field=models.ForeignKey(to='animal.AnimalGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dosingregime',
            name='dosed_animals',
            field=models.OneToOneField(related_name=b'dosed_animals', null=True, blank=True, to='animal.AnimalGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dosegroup',
            name='dose_regime',
            field=models.ForeignKey(related_name=b'doses', to='animal.DosingRegime'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dosegroup',
            name='dose_units',
            field=models.ForeignKey(to='animal.DoseUnits'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='animalgroup',
            name='dosing_regime',
            field=models.ForeignKey(blank=True, to='animal.DosingRegime', help_text=b'Specify an existing dosing regime or create a new dosing regime below', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='animalgroup',
            name='experiment',
            field=models.ForeignKey(to='animal.Experiment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='animalgroup',
            name='siblings',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='animal.AnimalGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='animalgroup',
            name='species',
            field=models.ForeignKey(to='animal.Species'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='animalgroup',
            name='strain',
            field=models.ForeignKey(to='animal.Strain'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aggregation',
            name='assessment',
            field=models.ForeignKey(related_name=b'aggregation', to='assessment.Assessment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aggregation',
            name='dose_units',
            field=models.ForeignKey(to='animal.DoseUnits'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aggregation',
            name='endpoints',
            field=models.ManyToManyField(help_text=b'All endpoints entered for assessment.', related_name=b'aggregation', to=b'animal.Endpoint'),
            preserve_default=True,
        ),
    ]
