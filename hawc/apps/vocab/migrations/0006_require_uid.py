from django.db import migrations, models


def set_fake_default(apps, schema_editor):
    Term = apps.get_model("vocab", "Term")
    terms = []
    for term in Term.objects.all():
        term.uid = term.id
        terms.append(term)
    Term.objects.bulk_update(terms, ["uid"])


class Migration(migrations.Migration):

    dependencies = [
        ("vocab", "0005_delete_comment"),
    ]

    operations = [
        migrations.RunPython(set_fake_default, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="term",
            name="uid",
            field=models.PositiveIntegerField(unique=True, blank=False, null=False),
        ),
    ]
