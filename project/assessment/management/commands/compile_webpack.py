import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand


HELP_TEXT = """Compile webpack bundles"""


class Command(BaseCommand):
    help = HELP_TEXT

    def handle(self, *args, **options):
        base = settings.PROJECT_PATH
        cmd = "npm run build".split(" ")
        subprocess.call(cmd, cwd=base)
