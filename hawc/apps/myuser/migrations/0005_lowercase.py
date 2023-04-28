import pandas as pd
from django.db import migrations


def lowercase_emails(apps, schema_editor):
    HAWCUser = apps.get_model("myuser", "HAWCUser")

    # preflight-check
    emails = pd.Series(list(HAWCUser.objects.all().values_list("email", flat=True)))
    if emails.size > 0:
        if emails.size != emails.str.lower().unique().size:
            raise ValueError()

    for user in HAWCUser.objects.all():
        email = user.email.lower()
        if user.email != email:
            user.email = email
            user.save()


def hero_access(apps, schema_editor):
    HAWCUser = apps.get_model("myuser", "UserProfile")
    HAWCUser.objects.filter(user__email__contains="@epa.gov").update(HERO_access=True)


class Migration(migrations.Migration):
    dependencies = [
        ("myuser", "0004_license_v2"),
    ]

    operations = [
        migrations.RunPython(lowercase_emails, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(hero_access, reverse_code=migrations.RunPython.noop),
    ]
