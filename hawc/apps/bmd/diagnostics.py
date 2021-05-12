import bmds
import numpy as np


def bmds2_service_healthcheck() -> bool:
    dataset = bmds.DichotomousDataset(
        doses=[0, 1.96, 5.69, 29.75], ns=[75, 49, 50, 49], incidences=[5, 1, 3, 14]
    )
    session = bmds.BMDS.versions["BMDS270"](dtype="D", dataset=dataset)
    session.add_model(bmds.constants.M_Logistic)
    session.execute()
    bmd = session.models[0].output["BMD"]
    return np.allclose(bmd, 17.4, atol=0.1)


def diagnostic_bmds2_execution(modeladmin, request, queryset):
    success = bmds2_service_healthcheck()
    if success:
        message = "BMDS2 remote execution completed successfully."
    else:
        message = "BMDS2 remote execution did not complete successfully."
    modeladmin.message_user(request, message)


diagnostic_bmds2_execution.short_description = "Diagnostic BMDS2 remote execution"
