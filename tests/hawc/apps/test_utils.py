"""
Utility toolbelt for testing HAWC.
"""

from hawc.apps.assessment.models import Log


def check_details_of_last_log_entry(obj_id: int, start_of_msg: str):
    """
    retrieve the latest log entry and check that the object_id/message look right.
    """
    log_entry = Log.objects.latest("id")
    assert log_entry.object_id == int(obj_id) and log_entry.message.startswith(start_of_msg)
