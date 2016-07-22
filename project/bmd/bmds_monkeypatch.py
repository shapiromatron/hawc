import bmds
import json
import requests

from django.conf import settings


# monkey-patch execution in bmds package
def get_dataset(session):
    runs = [
        {
            'id': model.id,
            'model_app_name': model.exe,
            'dfile': model.as_dfile()
        } for model in session._models
    ]

    return {
        'options': {
            'bmds_version': session.version,
            'emf_YN': False
        },
        'runs': runs
    }


def execute(self):
    host = settings.BMD_HOST
    data = get_dataset(self)

    # submit data
    url = '{}/Server-receiving.php'.format(host)
    r = requests.post(url, json.dumps(data))
    job_id = r.json()['BMDS_Service_Number']

    # execute run
    url = '{}/BMDS_execution.php'.format(host)
    data = {'bsn': job_id}
    requests.get(url, data)

    # get results
    url = '{}/Server-report.php'.format(host)
    data = {'BMDS_Service_Number': job_id}
    r = requests.get(url, data)

    # parse results for each model
    response = r.json()
    for model, resp in zip(self._models, response['BMDS_Results']):
        assert resp['id'] == model.id
        model.parse_results(resp['OUT_file_str'])

bmds.Session.execute = execute
