from django.conf import settings
from django.core.management.base import BaseCommand

from hawc.services.utils.git import git_sha

HELP_TEXT = """Set the .gitcommit file used for versioning"""


class Command(BaseCommand):
    help = HELP_TEXT

    def handle(self, *args, **options):
        text = git_sha(settings.PROJECT_ROOT)
        settings.GIT_COMMIT_FILE.write_text(text)
