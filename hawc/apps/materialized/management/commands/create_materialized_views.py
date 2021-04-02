from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import transaction

HELP_TEXT = """Create materialized views."""


class Command(BaseCommand):
    help = HELP_TEXT

    def add_arguments(self, parser):
        parser.add_argument(
            "mvs", type=str, nargs="*", help="Materialized view models to create.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        materialized = apps.get_app_config("materialized")

        if not options["mvs"]:
            for mv in materialized.get_models():
                mv.create()
        else:
            for mv in options["mvs"]:
                try:
                    materialized.get_model(mv).create()
                except LookupError:
                    raise CommandError(f"Model '{mv}' does not exist.")
