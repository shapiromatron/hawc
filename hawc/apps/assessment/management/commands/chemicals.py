import hashlib
import json
from typing import Any, Dict

from django.core.management.base import BaseCommand
from django.db import transaction

from hawc.apps.assessment.models import DSSTox
from hawc.services.epa.dsstox import DssSubstance


class Command(BaseCommand):
    help = """Crawls all existing DSSTox instances and updates with fresh data"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--refresh", action="store_true", help="Refresh exisiting DSSTox",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["refresh"]:
            dsstoxs = DSSTox.objects.all()
            dsstox_update = []
            for dsstox in dsstoxs.iterator():
                updated_dsstox = DssSubstance.create_from_dtxsid(dsstox.dtxsid)
                if dict_hash(dsstox.content) != dict_hash(updated_dsstox.content):
                    dsstox.content = updated_dsstox.content
                    dsstox_update.append(dsstox)
            if dsstox_update:
                DSSTox.objects.bulk_update(dsstox_update, ["content"])


def dict_hash(dict: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary"""
    dhash = hashlib.md5()
    encoded = json.dumps(dict, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()
