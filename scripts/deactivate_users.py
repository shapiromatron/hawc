"""
Mark old IDs as inactive; ensure that new ID users have the same id. Used
when a user creates multiple accounts and only wants to keep one.
"""
import logging
import os
import sys
from pathlib import Path

import django
from django.core import management
from django.db import transaction
from myuser.models import HAWCUser

ROOT = str(Path(__file__).parents[0].resolve())
sys.path.append(ROOT)
os.chdir(ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings.dev")
django.setup()
logger = logging.getLogger(__name__)


@transaction.atomic
def deactivate_user(new_id: int, old_ids: list[int]):
    """
    Mark old IDs as inactive; ensure that new ID users have the same id. Used
    when a user creates multiple accounts and only wants to keep one.

    Args:
        new_id (int): user ID to keep active
        old_ids (list[int]): user IDs to mark inactive
    """
    # deactivate old user ids, and reassign assessments for current user
    new_user = HAWCUser.objects.get(id=new_id)
    for old_user in HAWCUser.objects.filter(id__in=old_ids):
        for assessment in old_user.assessment_pms.all():
            if assessment not in new_user.assessment_pms.all():
                new_user.assessment_pms.add(assessment)
        old_user.assessment_pms.clear()

        for assessment in old_user.assessment_teams.all():
            if assessment not in new_user.assessment_teams.all():
                new_user.assessment_teams.add(assessment)
        old_user.assessment_teams.clear()

        for assessment in old_user.assessment_reviewers.all():
            if assessment not in new_user.assessment_reviewers.all():
                new_user.assessment_reviewers.add(assessment)
        old_user.assessment_reviewers.clear()

        old_user.is_active = False

        old_user.save()


if __name__ == "__main__":
    deactivate_user(new_id=123, old_ids=[456, 789])
    management.call_command("clear_cache")
