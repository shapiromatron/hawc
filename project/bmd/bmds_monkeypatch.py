import bmds
import json
import requests

from django.conf import settings


# monkey-patch execution in bmds package
def get_dataset(session):
    runs = [
        {
            'id': model.id,
            'model_app_name': model.model_name,
            'dfile': model.as_dfile()
        } for model in session._models
    ]

    return {
        'options': {
            'bmds_version': session.version,
            'emf_YN': 'True'
        },
        'runs': runs
    }


def get_dataset2(self):
    # temporary
    return {
        "options": {
            "bmds_version": "BMDS2601",
            "emf_YN": True,
        },
        "runs": [
            {
                "id": 29,
                "model_app_name": "DichoHill",
                "dfile": "Dichotomous-Hill \nBMDS_Model_Run \nC:/USEPA/BMDS/BMDS2601/Dorman2008/1-2008-AcroleinInhalation.dax \nC:/USEPA/BMDS/BMDS2601/Dorman2008/1-2008-Acrolein_Inhalation-DichHill-10Pct-4d.out \n4 \n500 0.00000001 0.00000001 0 1 1 0 0 \n0.1 0 0.95 \n-9999 -9999 -9999 -9999 \n0 \n-9999 -9999 -9999 -9999 \nDose Incidence NEGATIVE_RESPONSE \n0 0 12 \n0.2 0 12 \n0.6 7 5 \n1.8 11 0 \n"
            },
        ]
    }


def execute(self):
    host = settings.BMD_HOST
    data = get_dataset2(self)

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

    # todo - set results to session
    print(r.json())

    return r.json()


bmds.Session.execute = execute
