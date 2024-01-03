import sys
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands import migrate
from django.db.backends.base import creation
from django.test.utils import setup_databases

from hawc.apps.common.signals import ignore_signals


def load_iris_dataset() -> pd.DataFrame:
    return pd.read_csv(
        settings.PROJECT_ROOT / "tests/data/private-data/assessment/dataset-revision/iris.csv"
    )


class DisableMigrations:
    def __contains__(self, item: str) -> bool:
        return True

    def __getitem__(self, item: str) -> None:
        return None


class MigrateSilentCommand(migrate.Command):
    def handle(self, *args, **kwargs):
        kwargs["verbosity"] = 0
        return super().handle(*args, **kwargs)


class Command(BaseCommand):
    help = """Load the test database from a fixture."""

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

    def setup_environment(self) -> None:
        """Disable migrations like pytest-django does, but outside of pytest-django."""
        creation.TEST_DATABASE_PREFIX = ""
        migrate.Command = MigrateSilentCommand
        settings.MIGRATION_MODULES = DisableMigrations()
        self.stdout.write(self.style.HTTP_INFO("Migrating database schema..."))
        setup_databases(verbosity=0, interactive=False, keepdb=True)
        self.stdout.write(self.style.HTTP_INFO("Loading database fixture..."))
        call_command("loaddata", str(settings.TEST_DB_FIXTURE), verbosity=0)
        settings.MIGRATION_MODULES = {}
        self.stdout.write(self.style.HTTP_INFO("Writing migrations (fake)..."))
        call_command("migrate", verbosity=0, fake=True)

    def setup_test_environment(self) -> None:
        """Setup test environment within pytest environment."""
        self.stdout.write(self.style.HTTP_INFO("Migrating database schema..."))
        call_command("migrate", verbosity=0)
        self.stdout.write(self.style.HTTP_INFO("Flushing data..."))
        call_command("flush", verbosity=0, interactive=False)
        self.stdout.write(self.style.HTTP_INFO("Loading database fixture..."))
        call_command("loaddata", str(settings.TEST_DB_FIXTURE), verbosity=0)

    def handle(self, *args, **options):
        db_name = settings.DATABASES["default"]["NAME"]
        if not any(_ in db_name for _ in ["fixture", "test"]):
            raise CommandError("Must be using a test database to execute.")
        with ignore_signals():
            if "pytest" in sys.modules:
                self.setup_test_environment()
            else:
                self.setup_environment()

            self.stdout.write(self.style.HTTP_INFO("Recreating database views..."))
            call_command("recreate_views", verbosity=0)

            self.stdout.write(self.style.HTTP_INFO("Creating files..."))
            self.write_media_files()
