from django.conf import settings
from django.core.management.base import BaseCommand
import subprocess
import os


HELP_TEXT = """Set the .gitcommit file used for versioning"""


class Command(BaseCommand):
    help = HELP_TEXT

    def handle(self, *args, **options):
        cmd = "git log -1 --format=%H"
        commit = subprocess.check_output(cmd.split(), cwd=settings.PROJECT_ROOT).decode().strip()
        with open(os.path.join(settings.PROJECT_PATH, ".gitcommit"), "w") as f:
            f.write(commit)
