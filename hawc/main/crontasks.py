"""
Scheduled tasks using django-crontask.
These are the periodic tasks that were previously managed by celery beat.
"""
from django_tasks import task
from crontask import cron


# Worker healthcheck - every 5 minutes
@cron("*/5 * * * *")
@task
def worker_healthcheck():
    from hawc.apps.common import tasks as common_tasks

    common_tasks.worker_healthcheck()


# Destroy old API tokens - every 10 minutes
@cron("*/10 * * * *")
@task
def destroy_old_api_tokens():
    from hawc.apps.common import tasks as common_tasks

    common_tasks.destroy_old_api_tokens()


# Create initial revisions - daily at midnight
@cron("0 0 * * *")
@task
def create_initial_revisions():
    from hawc.apps.common import tasks as common_tasks

    common_tasks.create_initial_revisions()


# Update PubMed content - daily at midnight
@cron("0 0 * * *")
@task
def update_pubmed_content():
    from hawc.apps.lit import tasks as lit_tasks

    lit_tasks.fix_pubmed_without_content()


# Delete orphan relations - every 6 hours
@cron("0 */6 * * *")
@task
def delete_orphan_relations():
    from hawc.apps.assessment import tasks as assessment_tasks

    assessment_tasks.delete_orphan_relations(delete=False)


# Check and refresh materialized views - every 5 minutes
@cron("*/5 * * * *")
@task
def check_refresh_mvs():
    from hawc.apps.materialized import tasks as materialized_tasks

    materialized_tasks.refresh_all_mvs(force=False)


# Force refresh materialized views - daily at midnight
@cron("0 0 * * *")
@task
def refresh_mvs():
    from hawc.apps.materialized import tasks as materialized_tasks

    materialized_tasks.refresh_all_mvs(force=True)
