import bmds
import json
import requests

from django.conf import settings


def get_model_name(model):
    # special case for exponential models
    if hasattr(model, 'output_prefix'):
        return '{}_{}'.format(model.exe, model.output_prefix.lower())
    else:
        return model.exe


# monkey-patch execution in bmds package
def get_dataset(session):
    runs = [
        {
            'id': model.id,
            'model_app_name': get_model_name(model),
            'dfile': model.as_dfile()
        } for model in session._models
    ]

    return {
        'options': {
            'bmds_version': session.version,
            'emf_YN': True
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

        if 'base64_emf_str' in resp and len(resp['base64_emf_str']) > 0:
            model.plot_base64 = resp['base64_emf_str']

# TODO - fix completely
bmds.BMDS.execute = execute
