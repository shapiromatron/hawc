import bmds
from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
import numpy as np

logger = get_task_logger(__name__)


@shared_task
def execute(session_id):
    logger.info(f"BMD execution -> {session_id}")
    session = apps.get_model("bmd", "Session").objects.get(id=session_id)
    session.execute()


@shared_task
def bmds2_service_healthcheck() -> bool:
    """Run a simple dataset just to make sure the external webservice is operational.
    """
    dataset = bmds.DichotomousDataset(
        doses=[0, 1.96, 5.69, 29.75], ns=[75, 49, 50, 49], incidences=[5, 1, 3, 14]
    )
    session = bmds.BMDS.versions["BMDS270"](dtype="D", dataset=dataset)
    session.add_model(bmds.constants.M_Logistic)
    session.execute()
    return np.isclose(session.models[0].output["BMD"], 17.4, atol=0.1)
    # TODO - check and make sure this actually works!
