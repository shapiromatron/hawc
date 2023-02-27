# Generated by Django 3.2.18 on 2023-02-27 20:55

from django.db import migrations, models


def get_species_name(apps, schema_editor):
    AssessmentValue = apps.get_model("assessment", "AssessmentValue")
    Species = apps.get_model("assessment", "Species")
    values = AssessmentValue.objects.exclude(species_studied="")

    updates = []

    for value in values:
        try:
            species_id = int(value.species_studied)
            value.species_studied = Species.objects.get(pk=species_id).name
            updates.append(value)
        except Exception:
            continue

    AssessmentValue.objects.bulk_update(updates, ['species_studied'])


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0034_assessmentdetail_assessmentvalue'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assessmentvalue',
            name='non_adaf_value',
        ),
        migrations.AlterField(
            model_name='assessmentvalue',
            name='adaf',
            field=models.BooleanField(default=False, help_text='When checked, the ADAF note will appear as a footnote for the value', verbose_name='Apply ADAF?'),
        ),
        migrations.AlterField(
            model_name='assessmentvalue',
            name='duration',
            field=models.CharField(blank=True, help_text='Duration associated with the value (e.g., Chronic, Subchronic)', max_length=128, verbose_name='Value duration'),
        ),
        migrations.AlterField(
            model_name='assessmentvalue',
            name='species_studied',
            field=models.TextField(blank=True, default='', help_text='Provide information about the animal(s) studied, including species and strain information', verbose_name='Species and strain studied'),
            preserve_default=False,
        ),
        migrations.RunPython(get_species_name, migrations.RunPython.noop)
    ]
