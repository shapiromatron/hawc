from django.core.management.base import BaseCommand
from django.core.cache import cache


HELP_TEXT = """Completely clear cache."""


class Command(BaseCommand):
    help = HELP_TEXT

    def handle(self, *args, **options):
        cache.clear()
