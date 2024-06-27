from pathlib import Path

from django.core.management import call_command
from django.db import migrations, models
from django.utils import timezone


def load_fixture(apps, schema_editor):
    here = Path(__file__).parent
    fixtures = (here / "../fixtures").resolve()

    time = timezone.now()

    vocab = apps.get_model("eco", "Vocab")
    vocab.objects.filter(category=2).exclude(id__in=[197, 198]).update(deprecated_on=time)

    deprecated_nestedterms = [
        37,
        38,
        39,
        456,
        461,
        537,
        593,
        434,
        435,
        436,
        437,
        438,
        439,
        440,
        468,
        538,
        539,
    ]
    NestedTerm = apps.get_model("eco", "NestedTerm")
    NestedTerm.objects.filter(id__in=deprecated_nestedterms).update(deprecated_on=time)
    NestedTerm.objects.filter(id=457).update(name="fire and fire suppression")
    NestedTerm.objects.filter(id=60).update(name="Water withdrawal/abstraction")
    call_command("loaddata", str(fixtures / "updated_vocab.json"), app_label="eco")
    call_command("loaddata", str(fixtures / "updated_nestedterms.jsonl"), app_label="eco")


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
            name="habitats",
            field=models.ManyToManyField(
                help_text='Select one or more <a rel="noopener noreferrer" target="_blank" href="https://global-ecosystems.org/">IUCN Global Ecosystems</a> to which the evidence applies.',
                limit_choices_to={"category": 2, "deprecated_on": None},
                related_name="designs_by_habitat",
                to="eco.vocab",
            ),
        ),
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
