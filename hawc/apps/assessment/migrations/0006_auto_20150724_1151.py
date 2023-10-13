from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0005_auto_20150723_1544"),
    ]

    operations = [
        migrations.RenameField(
            model_name="doseunits",
            old_name="units",
            new_name="name",
        ),
        migrations.RemoveField(
            model_name="doseunits",
            name="administered",
        ),
        migrations.RemoveField(
            model_name="doseunits",
            name="converted",
        ),
        migrations.RemoveField(
            model_name="doseunits",
            name="hed",
        ),
        migrations.AlterModelOptions(
            name="doseunits",
            options={"ordering": ("name",), "verbose_name_plural": "dose units"},
        ),
    ]
