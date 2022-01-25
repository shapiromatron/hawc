import hashlib
import json
from typing import Any, Dict

from django.core.management.base import BaseCommand
from django.db import transaction

from hawc.apps.assessment.models import DSSTox
from hawc.services.epa.dsstox import DssSubstance


def _dict_hash(dict: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary"""
    dhash = hashlib.md5()
    encoded = json.dumps(dict, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


class Command(BaseCommand):
    help = """Chemical data operations"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--refresh", action="store_true", help="Refresh existing DSSTox",
        )

    def _refresh(self):
        updates = []
        for dsstox in DSSTox.objects.all().iterator():
            new_dsstox = DssSubstance.create_from_dtxsid(dsstox.dtxsid)
            existing_content = dsstox.content
            if _dict_hash(existing_content) != _dict_hash(new_dsstox.content):
                dsstox.content = new_dsstox.content
                updates.append(dsstox)
        if updates:
            DSSTox.objects.bulk_update(updates, ["content"])

    @transaction.atomic
    def handle(self, *args, **options):
        if options["refresh"]:
            self._refresh()
