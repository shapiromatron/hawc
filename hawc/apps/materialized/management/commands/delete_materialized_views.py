from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

HELP_TEXT = """Delete materialized views."""


class Command(BaseCommand):
    help = HELP_TEXT

    def add_arguments(self, parser):
        parser.add_argument(
            "mvs", type=str, nargs="*", help="Materialized view models to delete.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        materialized = apps.get_app_config("materialized")

        if not options["mvs"]:
            for mv in materialized.get_models():
                mv.delete()
        else:
            for mv in options["mvs"]:
                try:
                    materialized.get_model(mv).delete()
                except LookupError:
                    raise CommandError(f"Model '{mv}' does not exist.")
