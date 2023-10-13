from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invitro", "0002_auto_20150723_1542"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ivexperiment",
            name="cell_line",
        ),
        migrations.AddField(
            model_name="ivcelltype",
            name="culture_type",
            field=models.CharField(
                default="",
                max_length=2,
                choices=[
                    (b"nr", b"not reported"),
                    (b"im", b"Immortalized cell line"),
                    (b"pc", b"Primary culture"),
                    (b"tt", b"Transient transfected cell line"),
                    (b"st", b"Stably transfected cell line"),
                    (b"ts", b"Transient transfected into stably transfected cell line"),
                    (b"na", b"not applicable"),
                ],
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ivendpoint",
            name="values_estimated",
            field=models.BooleanField(
                default=False,
                help_text=b"Response values were estimated using a digital ruler or other methods",
            ),
        ),
        migrations.AddField(
            model_name="ivexperiment",
            name="cell_notes",
            field=models.TextField(
                help_text=b"Description of type of cell-line used (ex: primary cell-line, immortalized cell-line, stably transfected cell-line, transient transfected cell-line, etc.)",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="ivexperiment",
            name="has_naive_control",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="ivexperiment",
            name="name",
            field=models.CharField(default="", max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="observation_time",
            field=models.CharField(max_length=16, blank=True),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="overall_pattern",
            field=models.PositiveSmallIntegerField(
                default=0,
                choices=[
                    (0, b"not-available"),
                    (1, b"increase"),
                    (2, b"increase, then decrease"),
                    (6, b"increase, then no change"),
                    (3, b"decrease"),
                    (4, b"decrease, then increase"),
                    (7, b"decrease, then no change"),
                    (5, b"no clear pattern"),
                    (8, b"no change"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="ivendpoint",
            name="trend_test",
            field=models.PositiveSmallIntegerField(
                default=0,
                choices=[
                    (0, b"not reported"),
                    (1, b"not analyzed"),
                    (2, b"not applicable"),
                    (3, b"significant"),
                    (4, b"not significant"),
                ],
            ),
        ),
    ]
