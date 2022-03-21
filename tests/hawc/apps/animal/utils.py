import json

from ...study.tests.utils import build_studies_for_permission_testing
from .. import models


def build_experiments_for_permission_testing(obj):
    build_studies_for_permission_testing(obj)

    obj.experiment_working = models.Experiment.objects.create(
        study=obj.study_working,
        name="experiment name",
        type="Ac",
        description="No description.",
    )

    obj.experiment_final = models.Experiment.objects.create(
        study=obj.study_final_bioassay,
        name="experiment name",
        type="Ac",
        description="No description.",
    )


def build_animal_groups_for_permission_testing(obj):
    build_experiments_for_permission_testing(obj)

    obj.animal_group_working = models.AnimalGroup.objects.create(
        experiment=obj.experiment_working,
        name="animal group name",
        species=obj.species,
        strain=obj.strain,
        sex="M",
    )

    obj.animal_group_final = models.AnimalGroup.objects.create(
        experiment=obj.experiment_final,
        name="animal group name",
        species=obj.species,
        strain=obj.strain,
        sex="M",
    )


def build_dosing_regimes_for_permission_testing(obj):
    build_animal_groups_for_permission_testing(obj)

    obj.dosing_regime_working = models.DosingRegime.objects.create(
        dosed_animals=obj.animal_group_working,
        route_of_exposure="I",
        num_dose_groups=4,
        description="foo",
    )
    obj.dosing_regime_working.save()
    obj.animal_group_working.dosing_regime = obj.dosing_regime_working
    obj.animal_group_working.save()

    obj.dosing_regime_final = models.DosingRegime.objects.create(
        dosed_animals=obj.animal_group_final,
        route_of_exposure="I",
        num_dose_groups=4,
        description="foo",
    )
    obj.animal_group_final.dosing_regime = obj.dosing_regime_final
    obj.animal_group_final.save()


def build_endpoints_for_permission_testing(obj):
    build_dosing_regimes_for_permission_testing(obj)
    build_dose_groups(obj)
    obj.endpoint_working = models.Endpoint.objects.create(
        assessment=obj.assessment_working,
        animal_group=obj.animal_group_working,
        name="endpoint name",
        response_units="% affected",
        data_type="C",
        NOEL=1,
        LOEL=-999,
    )

    obj.endpoint_final = models.Endpoint.objects.create(
        assessment=obj.assessment_final,
        animal_group=obj.animal_group_final,
        name="endpoint name",
        response_units="% affected",
        data_type="C",
        NOEL=-999,
        LOEL=-999,
    )

    # now build endpoint groups
    endpoints = [obj.endpoint_working, obj.endpoint_final]
    egs = []
    for endpoint in endpoints:
        for i in range(4):
            egs.append(
                models.EndpointGroup(
                    dose_group_id=i,
                    n=20,
                    incidence=None,
                    response=i * 5.0,
                    variance=i * 1.0,
                    endpoint=endpoint,
                )
            )
    models.EndpointGroup.objects.bulk_create(egs)


def build_dosing_datasets_json(dose_units):
    # build a DoseGroup dataset with four dose groups
    dose_groups = []
    for i in range(4):
        dose_groups.append({"dose_units": dose_units.pk, "dose_group_id": i, "dose": i * 50})
    return json.dumps(dose_groups)


def build_dose_groups(obj):
    # build four dose-groups for each object
    regimes = [obj.dosing_regime_working, obj.dosing_regime_final]
    dgs = []
    for regime in regimes:
        for i in range(4):
            dgs.append(
                models.DoseGroup(
                    dose_regime=regime,
                    dose_units=obj.dose_units,
                    dose_group_id=i,
                    dose=i * 50.0,
                )
            )
    models.DoseGroup.objects.bulk_create(dgs)
