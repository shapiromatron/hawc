from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("study", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="study",
            name="study_identifier",
            field=models.CharField(
                help_text=b'Reference descriptor for assessment-tracking purposes (for example, "{Author, year, #EndNoteNumber}")',
                max_length=128,
                verbose_name=b"Internal study identifier",
                blank=True,
            ),
        ),
    ]
