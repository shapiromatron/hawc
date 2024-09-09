import json
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


def load_nested_terms(apps, schema_editor):
    now = timezone.now()

    # load the "real model" since we to use Treebeard manager methods
    from hawc.apps.eco.models import NestedTerm

    # rename
    NestedTerm.objects.filter(id=457).update(name="fire and fire suppression")
    NestedTerm.objects.filter(id=60).update(name="Water withdrawal/abstraction")

    # fmt: off
    # mark as deprecated
    NestedTerm.objects.filter(
        id__in=[
            37, 38, 39, 434, 435, 436, 437, 438, 439, 440, 456, 461, 468, 537, 538, 539, 593, 595
        ]
    ).update(deprecated_on=now)
    # fmt: on

    # load new terms. We can't use a django fixture because Treebeard reorders nodes and
    # may change the `path` of nodes based on name (for this model)
    additions = json.loads((fixtures / "nestedterms_2.json").read_text())
    for addition in additions:
        for i, parent_name in enumerate(addition["parents"]):
            if i == 0:
                parent = NestedTerm.objects.get(depth=1, name=parent_name)
            else:
                for child in parent.get_children():
                    if child.name == parent_name:
                        parent = child
                        break
        parent.add_child(**addition["fields"])


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
        migrations.RunPython(load_nested_terms, reverse_code=migrations.RunPython.noop),
    ]
