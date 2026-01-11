"""
Scheduled tasks using APScheduler.
These are the periodic tasks that were previously managed by celery beat.
"""
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


def setup_scheduler():
    """Setup the scheduler with all scheduled tasks"""
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)

    # Import task functions
    from hawc.apps.assessment import tasks as assessment_tasks
    from hawc.apps.common import tasks as common_tasks
    from hawc.apps.lit import tasks as lit_tasks
    from hawc.apps.materialized import tasks as materialized_tasks

    # Worker healthcheck - every 5 minutes
    scheduler.add_job(
        common_tasks.worker_healthcheck,
        CronTrigger.from_crontab("*/5 * * * *"),
        id="worker_healthcheck",
        name="Worker Healthcheck",
        replace_existing=True,
    )

    # Destroy old API tokens - every 10 minutes
    scheduler.add_job(
        common_tasks.destroy_old_api_tokens,
        CronTrigger.from_crontab("*/10 * * * *"),
        id="destroy_old_api_tokens",
        name="Destroy Old API Tokens",
        replace_existing=True,
    )

    # Create initial revisions - daily at midnight
    scheduler.add_job(
        common_tasks.create_initial_revisions,
        CronTrigger.from_crontab("0 0 * * *"),
        id="create_initial_revisions",
        name="Create Initial Revisions",
        replace_existing=True,
    )

    # Update PubMed content - daily at midnight
    scheduler.add_job(
        lit_tasks.fix_pubmed_without_content,
        CronTrigger.from_crontab("0 0 * * *"),
        id="fix_pubmed_without_content",
        name="Update PubMed Content",
        replace_existing=True,
    )

    # Delete orphan relations - every 6 hours
    scheduler.add_job(
        lambda: assessment_tasks.delete_orphan_relations(delete=False),
        CronTrigger.from_crontab("0 */6 * * *"),
        id="delete_orphan_relations",
        name="Delete Orphan Relations",
        replace_existing=True,
    )

    # Check and refresh materialized views - every 5 minutes
    scheduler.add_job(
        lambda: materialized_tasks.refresh_all_mvs(force=False),
        CronTrigger.from_crontab("*/5 * * * *"),
        id="check_refresh_mvs",
        name="Check Refresh MVs",
        replace_existing=True,
    )

    # Force refresh materialized views - daily at midnight
    scheduler.add_job(
        lambda: materialized_tasks.refresh_all_mvs(force=True),
        CronTrigger.from_crontab("0 0 * * *"),
        id="refresh_mvs",
        name="Refresh MVs",
        replace_existing=True,
    )

    return scheduler
