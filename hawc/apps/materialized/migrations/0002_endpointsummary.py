from django.db import migrations

from ..sql import EndpointSummary


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("materialized", "0001_initial"),
        ("animal", "0030_django31"),
    ]

    operations = [migrations.RunSQL(EndpointSummary.create, EndpointSummary.drop)]
