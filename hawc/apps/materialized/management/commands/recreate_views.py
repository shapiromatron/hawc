from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Create materialized views."

    @transaction.atomic
    def handle(self, *args, **options):
        materialized = apps.get_app_config("materialized")
        for mv in materialized.get_models():
            mv.drop()
            mv.create()
