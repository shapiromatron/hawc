from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from hawc.apps.common.signals import ignore_signals

HELP_TEXT = """Load the test database from a fixture."""


class Command(BaseCommand):
    help = HELP_TEXT

    def handle(self, *args, **options):

        if "test" not in settings.DATABASES["default"]["NAME"]:
            raise CommandError("Must be using a test database to execute.")

        with ignore_signals():
            call_command("migrate", verbosity=0)
            call_command("flush", verbosity=0, interactive=False)
            call_command("loaddata", str(settings.TEST_DB_FIXTURE), verbosity=1)
