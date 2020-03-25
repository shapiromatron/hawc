# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-09 23:47
from __future__ import unicode_literals

import json

from django.db import migrations, models
from litter_getter import hero, ris

from hawc.apps.lit.constants import HERO, PUBMED, RIS


def delete_external(apps, schema_editor):
    apps.get_model("lit", "Identifiers").objects.filter(database=0).delete()


def set_null_content(apps, schema_editor):
    num_updated = (
        apps.get_model("lit", "Identifiers").objects.filter(content="None").update(content="")
    )
    print(f"Updated {num_updated} items renaming content from 'None' to ''")


def update_identifier_content(apps, schema_editor):
    Identifiers = apps.get_model("lit", "Identifiers")

    qs = Identifiers.objects.filter(database=HERO)
    ntotal = qs.count()
    for idx, identifier in enumerate(qs.iterator()):
        if idx % 1000 == 0:
            print(f"Updating HERO identifier content {idx:,} of {ntotal:,}")
        if len(identifier.content) > 0:
            content = hero.parse_article(json.loads(json.loads(identifier.content)["json"]))
            identifier.content = json.dumps(content)
            identifier.save()

    qs = Identifiers.objects.filter(database=RIS)
    ntotal = qs.count()
    for idx, identifier in enumerate(qs.iterator()):
        if idx % 1000 == 0:
            print(f"Updating identifier content {idx:,} of {ntotal:,}")
        if len(identifier.content) > 0:
            parser = ris.ReferenceParser(json.loads(json.loads(identifier.content)["json"]))
            identifier.content = json.dumps(parser.format())
            identifier.save()


def set_authors(apps, schema_editor):
    Identifiers = apps.get_model("lit", "Identifiers")
    qs = Identifiers.objects.filter(database=[PUBMED, HERO])
    for idx, identifier in enumerate(qs.iterator()):
        if idx % 1000 == 0:
            print(f"Processing Pubmed/HERO {idx:,} ...")
        if len(identifier.content):
            content = json.loads(identifier.content)
            if "authors_list" in content:
                identifier.authors = ", ".join(content["authors"])
                identifier.save()

    qs = Identifiers.objects.filter(database=RIS)
    for idx, identifier in enumerate(qs.iterator()):
        if idx % 1000 == 0:
            print(f"Processing RIS {idx:,} ...")
        if len(identifier.content) > 0:
            identifier.authors = authors
            identifier.save()


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
        migrations.RunPython(update_identifier_content, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(set_authors, reverse_code=migrations.RunPython.noop),
    ]
