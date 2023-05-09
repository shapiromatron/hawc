"""
No operation migration. Stubbed in to replace obsolete load migration.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("vocab", "0002_review"),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]
