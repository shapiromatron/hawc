"""
The default BMDS python library requires execution on Windows; by default the
workaround is to submit data to bmds-server instance. However, HAWC proxies to
an intermediary server with a asynchronous response; therefore we need to
have a different workaround for execution.
"""
import time
from datetime import datetime

import requests
from bmds import BMDS
from bmds.monkeypatch import _get_payload, _set_results
from django.conf import settings


class JobException(Exception):
    pass


def run_job(url, data, api_token, interval=3, timeout=60):
    # https://gist.github.com/shapiromatron/0f04fa1f2626229cce28b06b02b7af4f
    with requests.Session() as s:
        s.headers.update(
            {
                "Authorization": f"Token {api_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        # initial job request
        response = s.post(url, data=data)
        if response.status_code in [400, 403]:
            raise JobException(response.json()["detail"])

        # poll response until job is complete or client-timeout
        wait_time = 0
        job_url = response.json()["url"]
        while True:
            time.sleep(interval)
            response = s.get(job_url).json()

            if response["is_finished"]:
                if response["has_errors"]:
                    raise JobException(response["errors"])
                else:
                    return response["outputs"]

            wait_time += interval
            if wait_time > timeout:
                raise JobException("Client timeout")


def execute(self):
    start_time = datetime.now()
    executable_models = []
    for model in self.models:
        model.execution_start = start_time
        if model.can_be_executed:
            executable_models.append(model)
        else:
            _set_results(model)

    if len(executable_models) == 0:
        return

    response = run_job(
        settings.BMDS_SUBMISSION_URL,
        _get_payload(executable_models),
        settings.BMDS_TOKEN,
        interval=3,
        timeout=120,
    )

    # parse results for each model
    for model, results in zip(executable_models, response):
        _set_results(model, results)


BMDS.execute = execute
