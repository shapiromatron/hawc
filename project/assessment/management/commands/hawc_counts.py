from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


HELP_TEXT = """Recursively iterate through all custom HAWC modules,
and print the number of items found in the database by object type."""


class Command(BaseCommand):
    args = ''
    help = HELP_TEXT

    def handle(self, *args, **options):
        if len(args)>0:
            raise CommandError("No inputs are taken for this command.")

        outputs = []
        outputs.append("HAWC object outputs\t{0}".format(datetime.now()))

        models = apps.get_models()
        for model in models:
            module = model.__module__
            name = model.__name__
            count = model.objects.count()
            outputs.append("{0}\t{1}\t{2}" \
               .format(module, name, count))

        for output in outputs:
            self.stdout.write(output)
