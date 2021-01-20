from django.conf import settings
from django.core.management.base import BaseCommand

from hawc.services.utils.git import Commit

HELP_TEXT = """Set the .gitcommit file used for versioning"""


class Command(BaseCommand):
    help = HELP_TEXT

    def handle(self, *args, **options):
        current = Commit.current(settings.PROJECT_ROOT)
        settings.GIT_COMMIT_FILE.write_text(current.json())
