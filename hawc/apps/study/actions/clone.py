from django.apps import apps

from ...animal.models import (
    AnimalGroup,
    Endpoint,
    EndpointGroup,
    Experiment,
)
from ...epiv2.models import (
    AdjustmentFactor,
    Chemical,
    DataExtraction,
    Design,
    Exposure,
    ExposureLevel,
    Outcome,
)
from ...riskofbias.models import (
    RiskOfBias,
    RiskOfBiasScoreOverrideObject,
)
from ..models import Study


def clone_study(src_study_id, dst_assessment_id):
    src_study = Study.objects.get(id=src_study_id)
    dst_study = Study.objects.get(id=src_study_id)

    # does not check for dupes
    dst_study.id = None
    dst_study.pk = None
    dst_study.assessment_id = dst_assessment_id
    dst_study.save()

    for attachment in src_study.attachments.all():
        attachment.id = None
        attachment.pk = None
        attachment.study_id = dst_study.id
        attachment.save()

    # copy list of identifiers (pubmed etc)
    src_identifiers = src_study.identifiers.all()
    dst_study.identifiers.add(*src_identifiers)
    dst_study.save()

    return {"study": {src_study_id: dst_study.id}}


def clone_animal_bioassay(src_study_id, dst_study_id):
    animal_map = {
        "experiment": {},
        "animalgroup": {},
        "dosingregime": {},
        "dosegroup": {},
        "endpoint": {},
        "endpointgroup": {},
    }
    src_study = Study.objects.get(id=src_study_id)
    dst_study = Study.objects.get(id=dst_study_id)
    src_experiments = Experiment.objects.filter(study=src_study)

    for experiment in src_experiments:
        src_experiment_id = experiment.id
        animal_groups = AnimalGroup.objects.filter(experiment=experiment)

        experiment.id = None
        experiment.pk = None
        experiment.study_id = dst_study_id
        experiment.save()
        animal_map["experiment"][src_experiment_id] = experiment.id

        for animal_group in animal_groups:
            dosing_regime = animal_group.dosing_regime
            dose_groups = dosing_regime.dose_groups
            endpoints = Endpoint.objects.filter(animal_group=animal_group)

            src_animal_group_id = animal_group.id
            src_dosing_regime_id = dosing_regime.id

            animal_group.id = None
            animal_group.pk = None
            animal_group.dosing_regime_id = None
            animal_group.experiment_id = experiment.id
            animal_group.save()
            animal_map["animalgroup"][src_animal_group_id] = animal_group.id

            dosing_regime.id = None
            dosing_regime.pk = None
            dosing_regime.dosed_animals_id = animal_group.id
            dosing_regime.save()
            animal_map["dosingregime"][src_dosing_regime_id] = dosing_regime.id

            animal_group.dosing_regime_id = dosing_regime.id
            animal_group.save()

            for dose_group in dose_groups:
                src_dose_group_id = dose_group.id

                dose_group.id = None
                dose_group.pk = None
                dose_group.dose_regime_id = dosing_regime.id
                dose_group.save()
                animal_map["dosegroup"][src_dose_group_id] = dose_group.id

            for endpoint in endpoints:
                src_endpoint_id = endpoint.id
                endpoint_groups = EndpointGroup.objects.filter(endpoint=endpoint)

                endpoint.id = None
                endpoint.pk = None
                endpoint.animal_group_id = animal_group.id
                endpoint.assessment_id = dst_study.assessment_id
                endpoint.save()
                animal_map["endpoint"][src_endpoint_id] = endpoint.id

                for endpoint_group in endpoint_groups:
                    src_endpoint_group_id = endpoint_group.id
                    endpoint_group.id = None
                    endpoint_group.pk = None
                    endpoint_group.endpoint_id = endpoint.id
                    endpoint_group.save()
                    animal_map["endpointgroup"][src_endpoint_group_id] = endpoint_group.id

    return animal_map


def clone_epiv2(src_study_id, dst_study_id):
    epiv2_map = {
        "design": {},
        "chemical": {},
        "exposure": {},
        "exposurelevel": {},
        "outcome": {},
        "adjustmentfactor": {},
        "dataextraction": {},
    }
    src_designs = Design.objects.filter(study_id=src_study_id)

    for src_design in src_designs:
        dst_design = Design.objects.get(id=src_design.id)
        dst_design.id = None
        dst_design.pk = None
        dst_design.study_id = dst_study_id
        dst_design.save()
        epiv2_map["design"][src_design.id] = dst_design.id

        # countries
        src_countries = src_design.countries.all()
        dst_design.countries.add(*src_countries)
        dst_design.save()

        src_chemicals = Chemical.objects.filter(design=src_design)
        for chem in src_chemicals:
            src_chem_id = chem.id
            chem.id = None
            chem.pk = None
            chem.design = dst_design
            chem.save()
            epiv2_map["chemical"][src_chem_id] = chem.id

        src_exposures = Exposure.objects.filter(design=src_design)
        for exposure in src_exposures:
            src_exposure_id = exposure.id
            exposure.id = None
            exposure.pk = None
            exposure.design = dst_design
            exposure.save()
            epiv2_map["exposure"][src_exposure_id] = exposure.id

        src_exposurelevels = ExposureLevel.objects.filter(design=src_design)
        for exposurelevel in src_exposurelevels:
            src_exposurelevel_id = exposurelevel.id
            exposurelevel.id = None
            exposurelevel.pk = None
            exposurelevel.design = dst_design
            exposurelevel.save()
            epiv2_map["exposurelevel"][src_exposurelevel_id] = exposurelevel.id

        src_outcomes = Outcome.objects.filter(design=src_design)
        for outcome in src_outcomes:
            src_outcome_id = outcome.id
            outcome.id = None
            outcome.pk = None
            outcome.design = dst_design
            outcome.save()
            epiv2_map["outcome"][src_outcome_id] = outcome.id

        src_adjustmentfactors = AdjustmentFactor.objects.filter(design=src_design)
        for adjustmentfactor in src_adjustmentfactors:
            src_adjustmentfactor_id = adjustmentfactor.id
            adjustmentfactor.id = None
            adjustmentfactor.pk = None
            adjustmentfactor.design = dst_design
            adjustmentfactor.save()
            epiv2_map["adjustmentfactor"][src_adjustmentfactor_id] = adjustmentfactor.id

        src_dataextractions = DataExtraction.objects.filter(design=src_design)
        for dataextraction in src_dataextractions:
            src_dataextraction_id = dataextraction.id
            dataextraction.id = None
            dataextraction.pk = None
            dataextraction.design = dst_design
            dataextraction.save()
            epiv2_map["dataextraction"][src_dataextraction_id] = dataextraction.id

    return epiv2_map


def clone_rob(src_study_id, dst_study_id, src_dst_metric_id_map, clone_map=None):
    rob_map = {"riskofbias": {}, "riskofbiasscore": {}, "riskofbiasscoreoverrideobject": {}}
    src_robs = RiskOfBias.objects.filter(study_id=src_study_id)

    for rob in src_robs:
        dst_rob = RiskOfBias.objects.get(id=rob.id)
        dst_rob.id = None
        dst_rob.pk = None
        dst_rob.study_id = dst_study_id
        dst_rob.save()
        rob_map["riskofbias"][rob.id] = dst_rob.id

        scores = rob.scores.all()
        for score in scores:
            src_score_id = score.id
            override = RiskOfBiasScoreOverrideObject.objects.filter(score=score)

            score.id = None
            score.pk = None
            score.riskofbias_id = dst_rob.id
            score.metric_id = int(src_dst_metric_id_map[str(score.metric_id)])
            score.save()
            rob_map["riskofbiasscore"][src_score_id] = score.id

            if override and clone_map:
                override = override[0]
                src_override_id = override.id
                src_override_type = override.content_type
                src_override_obj_id = override.content_object.id

                dst_override_model_name = clone_map.get(src_override_type.model, {})
                dst_override_id = dst_override_model_name.get(src_override_obj_id)
                if not dst_override_id:
                    continue

                dst_override_model = apps.get_model(
                    app_label=src_override_type.app_label, model_name=src_override_type.model
                )
                dst_override = dst_override_model.objects.get(id=dst_override_id)

                override.id = None
                override.pk = None
                override.score_id = score.id
                override.content_object = dst_override
                override.save()
                rob_map["riskofbiasscoreoverrideobject"][src_override_id] = override.id

    return rob_map
