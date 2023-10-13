from django.db import migrations


def strip_terms(apps, schema_editor):
    # we now enforce stripping on controlled vocabulary endpoint; update historical data
    Endpoint = apps.get_model("animal", "endpoint")
    for endpoint in Endpoint.objects.order_by("assessment_id", "id").all():
        system = endpoint.system.strip()
        organ = endpoint.organ.strip()
        effect = endpoint.effect.strip()
        effect_subtype = endpoint.effect_subtype.strip()
        name = endpoint.name.strip()

        if (
            system != endpoint.system
            or organ != endpoint.organ
            or effect != endpoint.effect
            or effect_subtype != endpoint.effect_subtype
            or name != endpoint.name
        ):
            print(
                f"Stripping vocabulary for assessment {endpoint.assessment_id} endpoint {endpoint.id}"
            )
            endpoint.system = system
            endpoint.organ = organ
            endpoint.effect = effect
            endpoint.effect_subtype = effect_subtype
            endpoint.name = name
            endpoint.save()


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0028_add_vocabulary"),
    ]

    operations = [
        migrations.RunPython(strip_terms, migrations.RunPython.noop),
    ]
