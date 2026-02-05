from django.core.management.base import BaseCommand

from hawc.main.crontasks import setup_scheduler


class Command(BaseCommand):
    help = "Run the task scheduler for periodic tasks"

    def handle(self, *args, **options):
        scheduler = setup_scheduler()
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
