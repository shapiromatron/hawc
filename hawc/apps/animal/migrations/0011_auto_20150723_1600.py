from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0010_auto_20150723_1536"),
        ("bmd", "0002_auto_20150723_1557"),
        ("epi", "0001_initial"),
        ("invitro", "0002_auto_20150723_1542"),
        ("summary", "0003_auto_20150723_1557"),
    ]

    state_operations = [
        migrations.DeleteModel(
            name="DoseUnits",
        ),
        migrations.AlterUniqueTogether(
            name="strain",
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name="strain",
            name="species",
        ),
        migrations.DeleteModel(
            name="Species",
        ),
        migrations.DeleteModel(
            name="Strain",
        ),
    ]

    operations = [migrations.SeparateDatabaseAndState(state_operations=state_operations)]
