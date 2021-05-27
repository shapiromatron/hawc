from django.db import migrations

from ..sql import MaterializedEndpoint


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("materialized", "0001_initial"),
        ("animal", "0030_django31"),
    ]

    operations = [migrations.RunSQL(MaterializedEndpoint.create, MaterializedEndpoint.drop)]
