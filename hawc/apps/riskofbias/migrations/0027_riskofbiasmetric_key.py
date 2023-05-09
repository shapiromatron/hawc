from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("riskofbias", "0026_fix_blank_text"),
    ]

    operations = [
        migrations.AlterField(
            model_name="riskofbiasmetric",
            name="name",
            field=models.CharField(help_text="Complete name of metric.", max_length=256),
        ),
        migrations.AlterField(
            model_name="riskofbiasmetric",
            name="short_name",
            field=models.CharField(
                blank=True, help_text="Short name, may be used in visualizations.", max_length=50
            ),
        ),
        migrations.AddField(
            model_name="riskofbiasmetric",
            name="key",
            field=models.CharField(
                blank=True,
                help_text="A unique identifier if it is from a standard protocol or procedure; can be used to match metrics across assessments.",
                max_length=8,
            ),
        ),
        migrations.AlterField(
            model_name="riskofbiasmetric",
            name="description",
            field=models.TextField(
                blank=True, help_text="Detailed instructions for how to apply this metric."
            ),
        ),
    ]
