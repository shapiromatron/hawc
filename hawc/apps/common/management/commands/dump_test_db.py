from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

HELP_TEXT = """Dump test database into a fixture."""


class Command(BaseCommand):
    help = HELP_TEXT

    def handle(self, *args, **options):

        if "test" not in settings.DATABASES["default"]["NAME"]:
            raise CommandError("Must be using a test database to execute.")

        f = StringIO()
        call_command("dumpdata", "contenttypes", format="yaml", indent=2, stdout=f)
        call_command("dumpdata", "myuser", format="yaml", indent=2, stdout=f)
        call_command("dumpdata", "assessment", format="yaml", indent=2, stdout=f)
        call_command("dumpdata", "lit", format="yaml", indent=2, stdout=f)
        call_command("dumpdata", "study", format="yaml", indent=2, stdout=f)

        Path(settings.TEST_DB_FIXTURE).parent.mkdir(exist_ok=True, parents=True)
        Path(settings.TEST_DB_FIXTURE).write_text(f.getvalue())
