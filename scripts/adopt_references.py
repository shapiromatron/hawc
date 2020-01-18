"""
Previously migrated references didn't have a Search associated with them and
could potentially be deleted if deemed orphaned. This script forces adoption.

```bash
cd /path/to/hawc/project
source ../venv/bin/activate
python ../scripts/adopt_references.py
```
"""
import os
from pathlib import Path
import sys

import django
from django.db import models, transaction
from django.core import management


ROOT = str((Path(__file__).parents[1] / "project").resolve())
sys.path.append(ROOT)
os.chdir(ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hawc.settings.local")

django.setup()

from lit.models import Reference, Search  # noqa: E402


@transaction.atomic
def adopt_studies(assessment_id: int):
    print(f"Fixing {assessment_id}")
    orphans = (
        Reference.objects.filter(assessment_id=assessment_id)
        .annotate(searches_count=models.Count("searches"))
        .filter(searches_count=0)
    )
    manual = Search.objects.get_manually_added(assessment=assessment_id)

    print(f"Found {orphans.count()} orphans")
    old_refcount = manual.references.count()
    manual.references.add(*orphans)
    new_refcount = manual.references.count()

    print(f"{old_refcount} + {orphans.count()} = {new_refcount}")
    assert old_refcount + orphans.count() == new_refcount


if __name__ == "__main__":
    adopt_studies(1)
    management.call_command("clear_cache")
