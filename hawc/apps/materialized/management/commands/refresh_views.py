from django.core.management.base import BaseCommand

from ...models import refresh_all_mvs


class Command(BaseCommand):
    help = "Force refresh materialized views."

    def handle(self, **options):
        message = "Starting materialized view refresh..."
        self.stdout.write(self.style.NOTICE(message))

        refresh_all_mvs(force=True)

        message = "Materialized views successfully refreshed!"
        self.stdout.write(self.style.SUCCESS(message))
