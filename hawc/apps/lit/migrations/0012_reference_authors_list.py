# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-09 23:47
from __future__ import unicode_literals

import json
import xml.etree.ElementTree as ET

from django.db import migrations, models

from hawc.apps.lit.constants import HERO, PUBMED, RIS
from hawc.services.epa import hero
from hawc.services.nih import pubmed
from hawc.services.utils import ris


def delete_external(apps, schema_editor):
    """
    Delete all external identifiers (no longer used)
    """
    apps.get_model("lit", "Identifiers").objects.filter(database=0).delete()


def set_null_content(apps, schema_editor):
    """
    Update identifiers to either return a valid JSON string or an empty string
    """
    num_updated = (
        apps.get_model("lit", "Identifiers").objects.filter(content="None").update(content="")
    )
    print(f"Updated {num_updated} items renaming content from 'None' to ''")


def reparse_identifiers(apps, schema_editor):
    """
    Re-parse identifiers from HERO/RIS using new parsing engine.
    """
    Identifiers = apps.get_model("lit", "Identifiers")

    qs = Identifiers.objects.filter(database=PUBMED)
    n_total = qs.count()
    updates = []
    for idx, identifier in enumerate(qs.iterator()):
        if idx % 5000 == 0:
            print(f"Updating PubMed identifier content {idx:,} of {n_total:,}")
        if len(identifier.content) > 0:
            tree = ET.fromstring(json.loads(identifier.content)["xml"])
            content = pubmed.PubMedParser.parse(tree)
            identifier.content = json.dumps(content)
            updates.append(identifier)

    print(f"Updating {len(updates):,} PubMed identifiers of {n_total:,}")
    Identifiers.objects.bulk_update(updates, ["content"], batch_size=5000)

    qs = Identifiers.objects.filter(database=HERO)
    n_total = qs.count()
    updates = []
    for idx, identifier in enumerate(qs.iterator()):
        if idx % 5000 == 0:
            print(f"Updating HERO identifier content {idx:,} of {n_total:,}")
        if len(identifier.content) > 0:
            content = hero.parse_article(json.loads(json.loads(identifier.content)["json"]))
            identifier.content = json.dumps(content)
            updates.append(identifier)

    print(f"Updating {len(updates):,} HERO identifiers of {n_total:,}")
    Identifiers.objects.bulk_update(updates, ["content"], batch_size=5000)

    qs = Identifiers.objects.filter(database=RIS)
    n_total = qs.count()
    updates = []
    for idx, identifier in enumerate(qs.iterator()):
        if idx % 5000 == 0:
            print(f"Updating identifier content {idx:,} of {n_total:,}")
        if len(identifier.content) > 0:
            parser = ris.ReferenceParser(json.loads(json.loads(identifier.content)["json"]))
            identifier.content = json.dumps(parser.format())
            updates.append(identifier)

    print(f"Updating {len(updates):,} references of {n_total:,}")
    Identifiers.objects.bulk_update(updates, ["content"], batch_size=5000)


def update_reference_authors(apps, schema_editor):
    """
    Set `authors` and `authors_short` for all references.
    """
    Reference = apps.get_model("lit", "Reference")
    qs = Reference.objects.all().prefetch_related("identifiers")
    n_total = Reference.objects.all().count()
    updates = []
    for idx, reference in enumerate(qs.iterator()):
        if idx % 5000 == 0:
            print(f"Updating reference authors {idx:,} of {n_total:,}")

        # get pubmed, or hero, or ris, if they exist, in that order
        identifier = (
            reference.identifiers.filter(database=PUBMED).first()
            or reference.identifiers.filter(database=HERO).first()
            or reference.identifiers.filter(database=RIS).first()
        )
        if identifier and identifier.content:
            content = json.loads(identifier.content)
            if "authors" in content:
                reference.authors = ", ".join(content["authors"])
                updates.append(reference)

    print(f"Updating {len(updates):,} RIS identifiers of {n_total:,}")
    Reference.objects.bulk_update(updates, ["authors"], batch_size=5000)


def update_pubmed_queries(apps, schema_editor):
    # convert ids from str to int
    PubMedQuery = apps.get_model("lit", "PubMedQuery")
    qs = PubMedQuery.objects.all()
    n_total = qs.count()
    updates = []
    for idx, query in enumerate(qs):
        if query.results:
            results = json.loads(query.results)
            results = dict(
                ids=[int(id) for id in results["ids"]],
                added=[int(id) for id in results["added"]],
                removed=[int(id) for id in results["removed"]],
            )
            query.results = json.dumps(results)
            updates.append(query)
            n_total += 1

    print(f"Updating {len(updates):,} PubMedQuery of {n_total:,}")
    PubMedQuery.objects.bulk_update(updates, ["results"], batch_size=5000)


class Migration(migrations.Migration):

    dependencies = [
        ("lit", "0011_auto_20190416_2035"),
    ]

    operations = [
        migrations.AlterField(
            model_name="identifiers",
            name="database",
            field=models.IntegerField(
                choices=[
                    (1, "PubMed"),
                    (2, "HERO"),
                    (3, "RIS (EndNote/Reference Manager)"),
                    (4, "DOI"),
                    (5, "Web of Science"),
                    (6, "Scopus"),
                    (7, "Embase"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="search",
            name="source",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "PubMed"),
                    (2, "HERO"),
                    (3, "RIS (EndNote/Reference Manager)"),
                    (4, "DOI"),
                    (5, "Web of Science"),
                    (6, "Scopus"),
                    (7, "Embase"),
                ],
                help_text="Database used to identify literature.",
            ),
        ),
        migrations.RenameField(
            model_name="reference", old_name="authors", new_name="authors_short",
        ),
        migrations.AlterField(
            model_name="reference",
            name="authors_short",
            field=models.TextField(
                blank=True, help_text='Short-text for to display (eg., "Smith et al.")'
            ),
        ),
        migrations.AddField(
            model_name="reference",
            name="authors",
            field=models.TextField(
                blank=True,
                help_text='The complete, comma separated authors list, (eg., "Smith JD, Tom JF, McFarlen PD")',
            ),
        ),
        migrations.RunPython(delete_external, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(set_null_content, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(reparse_identifiers, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(update_reference_authors, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(update_pubmed_queries, reverse_code=migrations.RunPython.noop),
    ]
