from collections import defaultdict

from pydantic import BaseModel, Field, model_validator

from ...assessment.models import Assessment
from ...common.views import create_object_log
from ...riskofbias.models import (
    RiskOfBias,
    RiskOfBiasMetric,
    RiskOfBiasScoreOverrideObject,
)
from ..models import Study


class RobCloneCopyMode:
    final_to_initial = "final-to-initial"
    final_to_final = "final-to-final"

    def final_flag(self):
        return True if self.final_flag else False


class CloneStudyDataValidation(BaseModel):
    study: set[int] = Field(min_length=1)
    study_bioassay: set[int]
    study_epi: set[int]
    study_rob: set[int]
    include_rob: bool = False
    copy_mode: RobCloneCopyMode | None
    metric_map: dict[int, int]

    @model_validator(mode="after")
    def validate_after(self):
        if self.include_rob is False and len(self.study_rob) > 0:
            raise ValueError("Cannot include RoB without a study selected for RoB")
        elif self.include_rob and (len(self.metric_map) == 0):
            raise ValueError("Cannot include RoB without a RoB mapping")
        elif self.include_rob and (self.copy_mode is None):
            raise ValueError("Cannot include RoB without a copy mode specified")
        return self

    def clone(self, user, context: dict):
        src_studies = context["studies"].filter(id__in=self.study)
        if self.include_rob:
            src_metrics = {el.id: el for el in context["src_metrics"]}
            dst_metrics = {el.id: el for el in context["dst_metrics"]}
            mapping = {
                src_metrics[key]: dst_metrics[value] for key, value in self.metric_map.items()
            }

        dst_assessment = context["assessment"]
        studies_map = defaultdict(dict)
        for study in src_studies:
            src_study, dst_study = clone_study(study, dst_assessment)
            studies_map["studies"][src_study] = dst_study
            study_map = {"study": {src_study.id: dst_study.id}}
            if src_study.id in self.study_bioassay:
                study_map["bioassay"] = clone_animal_bioassay(src_study, dst_study)
            if src_study.id in self.study_epi:
                study_map["epi"] = clone_epiv2(src_study, dst_study)
            if src_study.id in self.study_rob:
                study_map["riskofbias"] = clone_rob(src_study, dst_study, self, mapping, user)
            create_object_log(
                "Cloned",
                dst_study,
                dst_assessment.id,
                user.id,
                f"Cloned from assessment {src_study.assessment_id} study {src_study.id}",
            )
        return studies_map


def clone_study(src_study: Study, dst_assessment: Assessment) -> tuple[Study, Study]:
    identifiers = list(src_study.identifiers.all())
    attachments = list(src_study.attachments.all())

    # both pk and id must be set to None for these inherited models
    dst_study = src_study
    dst_study.pk = None
    dst_study.id = None
    dst_study.assessment = dst_assessment
    dst_study.save()

    for attachment in attachments:
        attachment.id = None
        attachment.study_id = dst_study.id
        attachment.save()

    # copy identifiers
    dst_study.identifiers.set(identifiers)

    return src_study, dst_study


def clone_animal_bioassay(src_study: Study, dst_study: Study) -> dict:
    animal_map = defaultdict(dict)
    experiments = list(src_study.experiments.all().order_by("id"))
    for experiment in experiments:
        src_experiment_id = experiment.id
        animal_groups = list(experiment.animal_groups.all().order_by("id"))

        experiment.id = None  # both pk and id must be set to None
        experiment.pk = None
        experiment.study_id = dst_study.id
        experiment.save()
        animal_map["experiment"][src_experiment_id] = experiment.id

        animal_groups_object_map = {}
        for animal_group in animal_groups:
            dosing_regime = animal_group.dosing_regime
            dose_groups = list(dosing_regime.dose_groups.all().order_by("id"))
            endpoints = list(animal_group.endpoints.all().order_by("id"))
            parents = list(
                animal_groups_object_map[group.id]
                for group in animal_group.parents.all().order_by("id")
            )

            src_animal_group_id = animal_group.id
            src_dosing_regime_id = dosing_regime.id

            animal_group.id = None
            animal_group.pk = None
            animal_group.dosing_regime_id = None
            animal_group.experiment_id = experiment.id
            animal_group.save()
            if parents:
                animal_group.set(parents)
            animal_map["animalgroup"][src_animal_group_id] = animal_group.id
            animal_groups_object_map[src_animal_group_id] = animal_group

            dosing_regime.id = None
            dosing_regime.pk = None
            if dosing_regime.dosed_animals_id:
                dosing_regime.dosed_animals_id = animal_group.id
            dosing_regime.save()
            animal_map["dosingregime"][src_dosing_regime_id] = dosing_regime.id

            if animal_group.dosing_regime_id:
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
                endpoint_groups = list(endpoint.groups.all().order_by("id"))
                effects = list(endpoint.effects.all())

                endpoint.id = None
                endpoint.pk = None
                endpoint.animal_group_id = animal_group.id
                endpoint.assessment_id = dst_study.assessment_id
                endpoint.save()
                endpoint.effects.set(effects)
                animal_map["endpoint"][src_endpoint_id] = endpoint.id

                for endpoint_group in endpoint_groups:
                    src_endpoint_group_id = endpoint_group.id
                    endpoint_group.id = None
                    endpoint_group.pk = None
                    endpoint_group.endpoint_id = endpoint.id
                    endpoint_group.save()
                    animal_map["endpointgroup"][src_endpoint_group_id] = endpoint_group.id

    return animal_map


def clone_epiv2(src_study: Study, dst_study: Study) -> dict:
    epiv2_map = defaultdict(dict)
    src_designs = list(src_study.designs.all().order_by("id"))

    for design in src_designs:
        src_design_id = design.id
        countries = list(design.countries.all().order_by("id"))
        chemicals = list(design.chemicals.all().order_by("id"))
        exposures = list(design.exposures.all().order_by("id"))
        exposurelevels = list(design.exposure_levels.all().order_by("id"))
        outcomes = list(design.outcomes.all().order_by("id"))
        adjustmentfactors = list(design.adjustment_factors.all().order_by("id"))
        dataextractions = list(design.data_extractions.all().order_by("id"))

        design.id = None
        design.pk = None
        design.study_id = dst_study.id
        design.save()
        design.countries.set(countries)
        epiv2_map["design"][src_design_id] = design.id

        for chem in chemicals:
            src_chem_id = chem.id
            chem.id = None
            chem.pk = None
            chem.design = design
            chem.save()
            epiv2_map["chemical"][src_chem_id] = chem.id

        for exposure in exposures:
            src_exposure_id = exposure.id
            exposure.id = None
            exposure.pk = None
            exposure.design = design
            exposure.save()
            epiv2_map["exposure"][src_exposure_id] = exposure.id

        for exposurelevel in exposurelevels:
            src_exposurelevel_id = exposurelevel.id
            exposurelevel.id = None
            exposurelevel.pk = None
            exposurelevel.design_id = design
            exposurelevel.chemical_id = epiv2_map["chemical"][exposurelevel.chemical_id]
            exposurelevel.exposure_measurement_id = epiv2_map["exposure"][
                exposurelevel.exposure_measurement_id
            ]
            exposurelevel.save()
            epiv2_map["exposurelevel"][src_exposurelevel_id] = exposurelevel.id

        for outcome in outcomes:
            src_outcome_id = outcome.id
            outcome.id = None
            outcome.pk = None
            outcome.design = design
            outcome.save()
            epiv2_map["outcome"][src_outcome_id] = outcome.id

        for adjustmentfactor in adjustmentfactors:
            src_adjustmentfactor_id = adjustmentfactor.id
            adjustmentfactor.id = None
            adjustmentfactor.pk = None
            adjustmentfactor.design = design
            adjustmentfactor.save()
            epiv2_map["adjustmentfactor"][src_adjustmentfactor_id] = adjustmentfactor.id

        for dataextraction in dataextractions:
            src_dataextraction_id = dataextraction.id
            dataextraction.id = None
            dataextraction.pk = None
            dataextraction.design = design

            dataextraction.outcome_id = epiv2_map["outcome"][dataextraction.outcome_id]
            dataextraction.exposure_level_id = epiv2_map["exposurelevel"][
                dataextraction.exposure_level_id
            ]
            if dataextraction.factors_id:
                dataextraction.factors_id = epiv2_map["adjustmentfactor"][dataextraction.factors_id]

            dataextraction.save()
            epiv2_map["dataextraction"][src_dataextraction_id] = dataextraction.id

    return epiv2_map


def clone_rob(
    src_study: Study,
    dst_study: Study,
    settings: CloneStudyDataValidation,
    metric_map: dict[RiskOfBiasMetric, RiskOfBiasMetric],
    user,
) -> dict:
    rob_map = defaultdict(dict)
    src_robs = list(src_study.riskofbiases.filter(active=True, final=True))

    for rob in src_robs:
        src_rob_id = rob.id
        src_scores = list(rob.scores.all())

        rob.id = None
        rob.pk = None
        rob.study_id = dst_study.id
        rob.author = user
        rob.final = settings.copy_mode.final_flag()
        rob.save()
        dst_scores = rob.build_scores(dst_study.assessment, dst_study)

        rob_map["riskofbias"][src_rob_id] = rob.id

        for score in scores:
        #     src_score_id = score.id
        #     override = RiskOfBiasScoreOverrideObject.objects.filter(score=score)

        #     score.id = None
        #     score.pk = None
        #     score.riskofbias_id = dst_rob.id
        #     score.metric_id = int(src_dst_metric_id_map[str(score.metric_id)])
        #     score.save()
        #     rob_map["riskofbiasscore"][src_score_id] = score.id

        #     if override and clone_map:
        #         override = override[0]
        #         src_override_id = override.id
        #         src_override_type = override.content_type
        #         src_override_obj_id = override.content_object.id

        #         dst_override_model_name = clone_map.get(src_override_type.model, {})
        #         dst_override_id = dst_override_model_name.get(src_override_obj_id)
        #         if not dst_override_id:
        #             continue

        #         dst_override_model = apps.get_model(
        #             app_label=src_override_type.app_label, model_name=src_override_type.model
        #         )
        #         dst_override = dst_override_model.objects.get(id=dst_override_id)

        #         override.id = None
        #         override.pk = None
        #         override.score_id = score.id
        #         override.content_object = dst_override
        #         override.save()
        #         rob_map["riskofbiasscoreoverrideobject"][src_override_id] = override.id

    return rob_map
