from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """Print the number of items found in the database by object type."""

    def handle(self, *args, **options):
        outputs = []
        outputs.append(f"HAWC object outputs\t{datetime.now()}")

        models = apps.get_models()
        for model in models:
            module = model.__module__
            name = model.__name__
            count = model.objects.count()
            outputs.append(f"{module}\t{name}\t{count}")

        for output in outputs:
            self.stdout.write(output)
