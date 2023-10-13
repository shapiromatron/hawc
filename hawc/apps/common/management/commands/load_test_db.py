from pathlib import Path

import pandas as pd
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from hawc.apps.common.signals import ignore_signals


def load_iris_dataset() -> pd.DataFrame:
    return pd.read_csv(
        settings.PROJECT_ROOT / "tests/data/private-data/assessment/dataset-revision/iris.csv"
    )


class Command(BaseCommand):
    help = """Load the test database from a fixture."""

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--ifempty",
            action="store_true",
            dest="ifempty",
            help="Only flush/load if database is empty",
        )

    def write_media_files(self):
        """
        Sync filesystem with database.

        Part of the database syncs media files which are written to the filesystem. This
        command ensures that files exist in the required paths with the current test-fixture.
        This doesn't check file equality, but just expected files exist where they should be.
        """
        df = load_iris_dataset()
        # write csvs
        for name in ["iris.csv", "iris_final.csv"]:
            fn = Path(settings.PRIVATE_DATA_ROOT) / f"assessment/dataset-revision/{name}"
            if not fn.exists():
                self.stdout.write(self.style.HTTP_INFO(f"Writing {fn}"))
                fn.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(fn, index=False)
        # write excels
        for name in ["iris.xlsx"]:
            fn = Path(settings.PRIVATE_DATA_ROOT) / f"assessment/dataset-revision/{name}"
            if not fn.exists():
                self.stdout.write(self.style.HTTP_INFO(f"Writing {fn}"))
                fn.parent.mkdir(parents=True, exist_ok=True)
                df.to_excel(fn, index=False)

    def handle(self, *args, **options):
        if not any(_ in settings.DATABASES["default"]["NAME"] for _ in ["fixture", "test"]):
            raise CommandError("Must be using a test database to execute.")

        with ignore_signals():
            self.stdout.write(self.style.HTTP_INFO("Migrating database schema..."))
            call_command("migrate", verbosity=0)

            if options["ifempty"] and get_user_model().objects.count() > 0:
                message = "Migrations complete; fixture not loaded (db not empty)"
            else:
                self.stdout.write(self.style.HTTP_INFO("Flushing data..."))
                call_command("flush", verbosity=0, interactive=False)

                self.stdout.write(self.style.HTTP_INFO("Loading database fixture..."))
                call_command("loaddata", str(settings.TEST_DB_FIXTURE), verbosity=1)

                self.stdout.write(self.style.HTTP_INFO("Loading database views..."))
                call_command("recreate_views", verbosity=1)

                self.stdout.write(self.style.HTTP_INFO("Creating files..."))
                self.write_media_files()

                message = "Migrations complete; fixture (re)applied"

            self.stdout.write(self.style.SUCCESS(message))
