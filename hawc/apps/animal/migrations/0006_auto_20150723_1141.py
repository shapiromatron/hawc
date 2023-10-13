from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0005_auto_20150723_1136"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="aggregation",
            name="assessment",
        ),
        migrations.RemoveField(
            model_name="aggregation",
            name="dose_units",
        ),
        migrations.RemoveField(
            model_name="aggregation",
            name="endpoints",
        ),
        migrations.AlterUniqueTogether(
            name="referencevalue",
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name="referencevalue",
            name="aggregation",
        ),
        migrations.RemoveField(
            model_name="referencevalue",
            name="assessment",
        ),
        migrations.RemoveField(
            model_name="referencevalue",
            name="units",
        ),
        migrations.AlterUniqueTogether(
            name="uncertaintyfactorendpoint",
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name="uncertaintyfactorendpoint",
            name="endpoint",
        ),
        migrations.AlterUniqueTogether(
            name="uncertaintyfactorrefval",
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name="uncertaintyfactorrefval",
            name="reference_value",
        ),
        migrations.DeleteModel(
            name="Aggregation",
        ),
        migrations.DeleteModel(
            name="ReferenceValue",
        ),
        migrations.DeleteModel(
            name="UncertaintyFactorEndpoint",
        ),
        migrations.DeleteModel(
            name="UncertaintyFactorRefVal",
        ),
    ]
