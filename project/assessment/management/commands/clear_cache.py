from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache


HELP_TEXT = """Completely clear cache."""


class Command(BaseCommand):
    args = ''
    help = HELP_TEXT

    def handle(self, *args, **options):
        if len(args)>0:
            raise CommandError("No inputs are taken for this command.")

        cache.clear()
        self.stdout.write('Cache cleared!')
