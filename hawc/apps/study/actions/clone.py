import json
from collections import defaultdict
from enum import StrEnum

from django.db import transaction
from pydantic import BaseModel, Field, model_validator

from ...assessment.models import Assessment
from ...common.views import create_object_log
from ...riskofbias.models import RiskOfBiasScore
from ..models import Study


class CloneRobCopyMode(StrEnum):
    final_to_initial = "final-to-initial"
    final_to_final = "final-to-final"

    def final_flag(self):
        return True if self == self.final_to_final else False


class CloneStudySettings(BaseModel):
    study: set[int] = Field(min_length=1)
    study_bioassay: set[int]
    study_epi: set[int]
    study_rob: set[int]
    include_rob: bool = False
    copy_mode: CloneRobCopyMode | None
    metric_map: dict[int, int]  # dst: src

    @model_validator(mode="after")
    def validate_after(self):
        if self.include_rob and len(self.study_rob) == 0:
            raise ValueError("Cannot include RoB without a study selected for RoB")
        elif self.include_rob and (len(self.metric_map) == 0):
            raise ValueError("Cannot include RoB without a RoB mapping")
        elif self.include_rob and (self.copy_mode is None):
            raise ValueError("Cannot include RoB without a copy mode specified")
        return self

    @transaction.atomic
    def clone(self, user, context: dict) -> dict[Study, tuple[Study, dict]]:
        dst_assessment = context["assessment"]
        src_studies = context["studies"].filter(id__in=self.study)
        studies_map = {}
        for src_study in src_studies:
            mapping = defaultdict(dict)
            study_map, dst_study = _clone_study(src_study, dst_assessment)
            mapping["study"] = study_map
            if src_study.id in self.study_bioassay:
                mapping["animal"] = _clone_animal_bioassay(src_study, dst_study)
            if src_study.id in self.study_epi:
                mapping["epiv2"] = _clone_epiv2(src_study, dst_study)
            if src_study.id in self.study_rob:
                mapping["riskofbias"] = _clone_rob(src_study, dst_study, self, user, mapping)
            create_object_log(
                "Cloned",
                dst_study,
                dst_assessment.id,
                user.id,
                f"Cloned from assessment {src_study.assessment_id} study {src_study.id}. Mapping: {json.dumps(mapping)}",
                use_reversion=False,
            )
            studies_map[src_study] = (dst_study, mapping)
        return studies_map


type StudyMapping = dict[str, dict[str, dict[int, int]]]
type StudyAppMapping = dict[str, dict[int, int]]


def _clone_study(src_study: Study, dst_assessment: Assessment) -> tuple[StudyAppMapping, Study]:
    study_map = defaultdict(dict)
    src_study_id = src_study.pk
    identifiers = list(src_study.identifiers.all())
    attachments = list(src_study.attachments.all())

    # both pk and id must be set to None for these inherited models
    dst_study = Study.objects.get(id=src_study_id)  # get a clone to mutate
    dst_study.pk = None
    dst_study.id = None
    dst_study.assessment = dst_assessment
    dst_study.save()
    study_map["study"][src_study_id] = dst_study.id

    for attachment in attachments:
        src_attachment_id = attachment.id
        attachment.id = None
        attachment.study_id = dst_study.id
        attachment.save()
        study_map["attachment"][src_attachment_id] = attachment.id

    # copy identifiers
    dst_study.identifiers.set(identifiers)

    return study_map, dst_study


def _clone_animal_bioassay(src_study: Study, dst_study: Study) -> StudyAppMapping:
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
                animal_group.parents.set(parents)
            animal_map["animalgroup"][src_animal_group_id] = animal_group.id
            animal_groups_object_map[src_animal_group_id] = animal_group

            cloned_dr = animal_map.get("dosingregime", {}).get(src_dosing_regime_id)
            if cloned_dr is not None:
                dst_dosing_regime_id = cloned_dr
            else:
                dosing_regime.id = None
                dosing_regime.pk = None
                if dosing_regime.dosed_animals_id:
                    dosing_regime.dosed_animals_id = animal_group.id
                dosing_regime.save()

                animal_map["dosingregime"][src_dosing_regime_id] = dosing_regime.id
                dst_dosing_regime_id = dosing_regime.id

                for dose_group in dose_groups:
                    src_dose_group_id = dose_group.id

                    dose_group.id = None
                    dose_group.pk = None
                    dose_group.dose_regime_id = dst_dosing_regime_id
                    dose_group.save()
                    animal_map["dosegroup"][src_dose_group_id] = dose_group.id

            if src_dosing_regime_id:
                animal_group.dosing_regime_id = dst_dosing_regime_id
                animal_group.save()

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


def _clone_epiv2(src_study: Study, dst_study: Study) -> StudyAppMapping:
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
            exposurelevel.design_id = design.id
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
            outcome.design_id = design.id
            outcome.save()
            epiv2_map["outcome"][src_outcome_id] = outcome.id

        for adjustmentfactor in adjustmentfactors:
            src_adjustmentfactor_id = adjustmentfactor.id
            adjustmentfactor.id = None
            adjustmentfactor.pk = None
            adjustmentfactor.design_id = design.id
            adjustmentfactor.save()
            epiv2_map["adjustmentfactor"][src_adjustmentfactor_id] = adjustmentfactor.id

        for dataextraction in dataextractions:
            src_dataextraction_id = dataextraction.id
            dataextraction.id = None
            dataextraction.pk = None
            dataextraction.design_id = design.id

            dataextraction.outcome_id = epiv2_map["outcome"][dataextraction.outcome_id]
            dataextraction.exposure_level_id = epiv2_map["exposurelevel"][
                dataextraction.exposure_level_id
            ]
            if dataextraction.factors_id:
                dataextraction.factors_id = epiv2_map["adjustmentfactor"][dataextraction.factors_id]

            dataextraction.save()
            epiv2_map["dataextraction"][src_dataextraction_id] = dataextraction.id

    return epiv2_map


def _clone_rob(
    src_study: Study,
    dst_study: Study,
    settings: CloneStudySettings,
    user,
    study_map: StudyMapping,
) -> StudyAppMapping:
    rob_map = defaultdict(dict)
    try:
        rob = src_study.riskofbiases.get(active=True, final=True)
    except src_study.riskofbiases.model.DoesNotExist:
        raise ValueError(f"No active final evaluation available for {src_study}") from None

    src_rob_id = rob.id
    src_scores = list(rob.scores.all().prefetch_related("overridden_objects"))

    rob.id = None
    rob.pk = None
    rob.study_id = dst_study.id
    rob.author = user
    rob.final = settings.copy_mode.final_flag()
    rob.save()
    dst_scores = rob.build_scores(dst_study.assessment, dst_study)

    rob_map["riskofbias"][src_rob_id] = rob.id
    for score in dst_scores:
        # check if there's a metric map in the mapping
        src_metric_id = settings.metric_map.get(score.metric_id)
        if src_metric_id is None:
            continue

        # find matching source scores for this src study
        src_matched_scores = [s for s in src_scores if s.metric_id == src_metric_id]
        if src_matched_scores is None:
            continue

        # copy default score if one exists
        src_defaults = [s for s in src_matched_scores if s.is_default is True]
        src_extras = [s for s in src_matched_scores if s.is_default is False]
        if src_defaults:
            if len(src_defaults) > 1:
                raise ValueError("Bad state; non unique (study, metric, default score)")
            _rob_score_update(src_defaults[0], score, rob_map, study_map)

        # copy extra scores if they exist
        if src_extras:
            for src_extra in src_extras:
                score.pk = None
                score.id = None
                score.is_default = False
                _rob_score_update(src_extra, score, rob_map, study_map)

    return rob_map


def _rob_score_update(
    src_score: RiskOfBiasScore,
    dst_score: RiskOfBiasScore,
    rob_map: StudyAppMapping,
    study_map: StudyMapping,
):
    # set score attributes
    for field in ["label", "score", "bias_direction", "notes"]:
        setattr(dst_score, field, getattr(src_score, field))
    dst_score.save()
    rob_map["riskofbiasscore"][src_score.id] = dst_score.id

    # set override attributes
    src_overrides = list(src_score.overridden_objects.all())
    for override in src_overrides:
        # try to find object match. Get app, then model, the object ID
        ct = override.content_type
        dst_object_id = study_map.get(ct.app_label, {}).get(ct.model, {}).get(override.object_id)
        if dst_object_id is None:
            continue
        src_override_id = override.id

        override.pk = None
        override.id = None
        override.score_id = dst_score.id
        override.object_id = dst_object_id
        override.save()
        rob_map["riskofbiasscoreoverrideobject"][src_override_id] = override.id
