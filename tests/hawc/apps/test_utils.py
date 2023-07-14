"""
Utility toolbelt for testing HAWC.
"""

import json
from pathlib import Path

from hawc.apps.assessment.models import Log

DATA_ROOT = Path(__file__).parents[2] / "data/api"


def check_details_of_last_log_entry(obj_id: int, start_of_msg: str):
    """
    retrieve the latest log entry and check that the object_id/message look right.
    """
    log_entry = Log.objects.latest("id")
    assert log_entry.object_id == int(obj_id) and log_entry.message.startswith(start_of_msg)


def check_api_json_data(data: dict, key: str, rewrite_data_files: bool):
    fn = Path(DATA_ROOT / key)
    if rewrite_data_files:
        fn.write_text(json.dumps(data, indent=2, sort_keys=True))
    assert json.loads(fn.read_text()) == data


def check_api_403(client, url, format="json"):
    response = client.get(url, format=format)
    assert response.status_code == 403
    return response


def check_api_200(client, url, format="json"):
    response = client.get(url, format=format)
    assert response.status_code == 200
    return response
