from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache


HELP_TEXT = """Completely clear cache."""


class Command(BaseCommand):
    help = HELP_TEXT

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write('Cache cleared!')
