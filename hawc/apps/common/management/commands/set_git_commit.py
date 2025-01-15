from django.conf import settings
from django.core.management.base import BaseCommand

from .....services.utils.git import Commit


class Command(BaseCommand):
    help = """Set the gitcommit.json file used for versioning"""

    def handle(self, *args, **options):
        current = Commit.current(settings.PROJECT_ROOT)
        settings.GIT_COMMIT_FILE.write_text(current.model_dump_json())
