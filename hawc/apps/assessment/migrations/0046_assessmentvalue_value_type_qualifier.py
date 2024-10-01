# Generated by Django 5.1.1 on 2024-09-25 19:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0045_assessment_labels"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessmentvalue",
            name="value_type_qualifier",
            field=models.CharField(
                blank=True,
                help_text="A optional qualifier displayed with the Value Type. E.g., Adult-based. This value is typically used to clarify when a value has an adjustment applied like an ADAF.",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="assessmentvalue",
            name="adaf",
            field=models.BooleanField(
                default=False,
                help_text="When checked, the ADAF note will appear as a footnote for the value. Add supporting information about ADAF in the comments.",
                verbose_name="ADAF has been applied?",
            ),
        ),
    ]
