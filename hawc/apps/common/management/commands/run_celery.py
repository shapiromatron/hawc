from celery.bin.celery import main
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """Execute celery from django management command"""

    def run_from_argv(self, argv):
        commands = argv[2:]
        commands.insert(0, "celery")
        main(commands)
