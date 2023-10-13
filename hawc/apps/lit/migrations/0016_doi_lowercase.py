from collections import defaultdict

from django.db import migrations
from django.db.models import F, Func


def get_duplicates(Identifiers) -> list[list[int]]:
    # return lists of Identifiers which have duplicative DOI values
    d = defaultdict(list)
    for ident in Identifiers.objects.filter(database=4):
        d[ident.unique_id.lower()].append(ident.id)
    return [el for el in d.values() if len(el) > 1]


def update_references(Identifiers, doi_duplicates):
    # Update references associated with the identifiers to be deleted to be replaced by those
    # which will be unchanged.
    for ids in doi_duplicates:
        idents = Identifiers.objects.filter(id__in=ids).prefetch_related("references")
        # find the "target" Identifier which we relate other References to
        target = idents[0]
        for ident in idents:
            if ident.unique_id == ident.unique_id.lower():
                target = ident
        # add the "target" and remove others, then delete the others
        for ident in idents:
            if ident.id == target.id:
                continue
            for ref in ident.references.all():
                ref.identifiers.add(target)
                ref.identifiers.remove(ident)
            ident.delete()


def set_doi_lowercase(apps, schema_editor):
    # Cleanup prior to lowercasing to ensure that our unique value restriction is valid
    Identifiers = apps.get_model("lit", "Identifiers")
    doi_duplicates = get_duplicates(Identifiers)
    update_references(Identifiers, doi_duplicates)
    Identifiers.objects.filter(database=4).update(unique_id=Func(F("unique_id"), function="LOWER"))


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0015_unaccent"),
    ]

    operations = [
        migrations.RunPython(set_doi_lowercase, reverse_code=migrations.RunPython.noop),
    ]
