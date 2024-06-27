from pathlib import Path

import django.db.models.deletion
from django.core.management import call_command
from django.db import migrations, models
from django.utils import timezone

here = Path(__file__).parent
fixtures = (here / "../fixtures").resolve()


def load_vocab(apps, schema_editor):
    now = timezone.now()

    # deprecate existing
    vocab = apps.get_model("eco", "Vocab")
    vocab.objects.filter(category=2).exclude(id__in=[197, 198]).update(deprecated_on=now)

    # load new values
    call_command("loaddata", str(fixtures / "vocab_2.jsonl"), app_label="eco")


class Migration(migrations.Migration):
    dependencies = [
        ("eco", "0005_remove_restraints"),
    ]

    operations = [
        migrations.AddField(
            model_name="nestedterm",
            name="deprecated_on",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="vocab",
            name="deprecated_on",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="design",
            name="climates",
            field=models.ManyToManyField(
                help_text='Select one or more <a rel="noopener noreferrer" target="_blank" href="http://koeppen-geiger.vu-wien.ac.at/present.htm">Koppen climate classifications</a> to which the evidence applies',
                limit_choices_to={"category": 11, "deprecated_on": None},
                related_name="designs_by_climate",
                to="eco.vocab",
            ),
        ),
        migrations.AlterField(
            model_name="design",
            name="design",
            field=models.ForeignKey(
                help_text="Select study design",
                limit_choices_to={"category": 0, "deprecated_on": None},
                on_delete=django.db.models.deletion.CASCADE,
                related_name="designs_by_type",
                to="eco.vocab",
            ),
        ),
        migrations.AlterField(
            model_name="design",
            name="ecoregions",
            field=models.ManyToManyField(
                blank=True,
                help_text='Select one or more <a rel="noopener noreferrer" target="_blank" href="https://www.epa.gov/eco-research/level-iii-and-iv-ecoregions-continental-united-states">Level III Ecoregions</a> from the continental US, if known',
                limit_choices_to={"category": 12, "deprecated_on": None},
                related_name="designs_by_ecoregion",
                to="eco.vocab",
            ),
        ),
        migrations.AlterField(
            model_name="design",
            name="habitats",
            field=models.ManyToManyField(
                help_text='Select one or more <a rel="noopener noreferrer" target="_blank" href="https://global-ecosystems.org/">IUCN Global Ecosystems</a> to which the evidence applies.',
                limit_choices_to={"category": 2, "deprecated_on": None},
                related_name="designs_by_habitat",
                to="eco.vocab",
            ),
        ),
        migrations.AlterField(
            model_name="design",
            name="study_setting",
            field=models.ForeignKey(
                help_text="Select the setting in which evidence was generated",
                limit_choices_to={"category": 1, "deprecated_on": None},
                on_delete=django.db.models.deletion.CASCADE,
                related_name="designs_by_setting",
                to="eco.vocab",
            ),
        ),
        migrations.RunPython(load_vocab, reverse_code=migrations.RunPython.noop),
    ]
