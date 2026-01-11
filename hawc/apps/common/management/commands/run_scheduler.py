"""Management command to run the task scheduler."""
import logging

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run the task scheduler for periodic tasks"

    def handle(self, *args, **options):
        from hawc.main.crontasks import setup_scheduler

        logger.info("Starting task scheduler...")
        scheduler = setup_scheduler()

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down scheduler...")
            scheduler.shutdown()
