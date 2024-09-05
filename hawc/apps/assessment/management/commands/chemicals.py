import hashlib
import json
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from .....services.epa.dsstox import DssSubstance
from ...models import DSSTox


def _dict_hash(dict: dict[str, Any]) -> str:
    """MD5 hash of a dictionary"""
    dhash = hashlib.md5(usedforsecurity=False)
    encoded = json.dumps(dict, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


class Command(BaseCommand):
    help = """Chemical data operations"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="Refresh existing DSSTox",
        )

    def _refresh(self):
        updates = []
        for dsstox in DSSTox.objects.all().order_by("dtxsid").iterator():
            self.stdout.write(f"Checking {dsstox.dtxsid}")
            new_dsstox = DssSubstance.create_from_dtxsid(dsstox.dtxsid)
            if _dict_hash(dsstox.content) != _dict_hash(new_dsstox.content):
                dsstox.content = new_dsstox.content
                updates.append(dsstox)
        if updates:
            ids = ", ".join([d.dtxsid for d in updates])
            DSSTox.objects.bulk_update(updates, ["content"])
            self.stdout.write(f"Updated {ids}")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["refresh"]:
            self._refresh()
