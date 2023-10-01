import pandas as pd
from django.db.models import QuerySet

from ..common.models import BaseManager, replace_null, sql_display, str_m2m
from ..study.managers import study_df_annotations, study_df_mapping
from .constants import ChangeTrajectory


class DesignQuerySet(QuerySet):
    def published_only(self, published_only: bool):
        return self.filter(study__published=True) if published_only else self


class DesignManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return DesignQuerySet(self.model, using=self._db)

    def study_df(self, study_qs: QuerySet) -> pd.DataFrame:
        """Returns a data frame, one row per study in study queryset

        Args:
            study_qs (QuerySet): A study queryset of studies
        """
        mapping = {
            **study_df_mapping("study-"),
            "designs": "eco_designs_str",
            "design_types": "eco_design_types_str",
            "study_settings": "eco_study_settings_str",
            "countries": "countries_str",
            "states": "states_str",
            "ecoregions": "ecoregions_str",
            "habitats": "habitats_str",
            "climates": "climates_str",
            "causes": "eco_causes_str",
            "effects": "eco_effects_str",
        }
        qs = study_qs.annotate(
            **study_df_annotations(),
            eco_designs_str=str_m2m("eco_designs__name"),
            eco_design_types_str=str_m2m("eco_designs__design__value"),
            eco_study_settings_str=str_m2m("eco_designs__study_setting__value"),
            countries_str=str_m2m("eco_designs__countries__name"),
            states_str=str_m2m("eco_designs__states__name"),
            ecoregions_str=str_m2m("eco_designs__ecoregions__value"),
            habitats_str=str_m2m("eco_designs__habitats__value"),
            climates_str=str_m2m("eco_designs__climates__value"),
            eco_causes_str=str_m2m("eco_causes__name"),
            eco_effects_str=str_m2m("eco_effects__name"),
        ).values_list(*list(mapping.values()))
        return (
            pd.DataFrame(data=qs, columns=list(mapping.keys()))
            .drop(
                columns=[
                    "study-coi_reported",
                    "study-coi_details",
                    "study-funding_source",
                    "study-study_identifier",
                    "study-contact_author",
                    "study-ask_author",
                    "study-published",
                    "study-summary",
                ]
            )
            .rename(
                columns={
                    "study-id": "study_id",
                    "study-PMID": "pubmed_id",
                    "study-HERO ID": "hero_id",
                    "study-DOI": "doi",
                    "study-short_citation": "short_citation",
                    "study-full_citation": "full_citation",
                }
            )
        )


class CauseQuerySet(QuerySet):
    def published_only(self, published_only: bool):
        return self.filter(study__published=True) if published_only else self


class CauseManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return CauseQuerySet(self.model, using=self._db)


class EffectQuerySet(QuerySet):
    def published_only(self, published_only: bool):
        return self.filter(study__published=True) if published_only else self


class EffectManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return EffectQuerySet(self.model, using=self._db)


class ResultQuerySet(QuerySet):
    def published_only(self, published_only: bool):
        return self.filter(design__study__published=True) if published_only else self

    def complete(self):
        return self.select_related(
            "design__study",
            "design__study_setting",
            "cause__term",
            "cause__biological_organization",
            "effect__term",
            "effect__biological_organization",
            "statistical_sig_type",
            "measure_type",
            "variability",
        ).prefetch_related(
            "design__countries",
            "design__states",
            "design__ecoregions",
            "design__habitats",
            "design__climates",
        )

    def complete_df(self) -> pd.DataFrame:
        mapping = {
            # study
            **study_df_mapping("study-", "design__study__"),
            # design
            "design-id": "design__pk",
            "design-name": "design__name",
            "design-design_type": "design__design__value",
            "design-study_setting": "design__study_setting__value",
            "design-countries": "design__countries__name",
            "design-states": "design__states__name",
            "design-ecoregions": "design__ecoregions__value",
            "design-habitats": "design__habitats__value",
            "design-habitats_as_reported": "design__habitats_as_reported",
            "design-climates": "design__climates__value",
            "design-climates_as_reported": "design__climates_as_reported",
            "design-comments": "design__comments",
            "design-created": "design__created",
            "design-last_updated": "design__last_updated",
            # cause
            "cause-id": "cause__pk",
            "cause-name": "cause__name",
            "cause-term": "cause__term__name",
            "cause-biological-organization": replace_null("cause__biological_organization__value"),
            "cause-species": "cause__species",
            "cause-level": "cause__level",
            "cause-level_value": "cause__level_value",
            "cause-level_units": "cause__level_units",
            "cause-duration": "cause__duration",
            "cause-duration_value": "cause__duration_value",
            "cause-duration_units": "cause__duration_units",
            "cause-exposure": "cause__exposure",
            "cause-exposure_value": "cause__exposure_value",
            "cause-exposure_units": "cause__exposure_units",
            "cause-as_reported": "cause__as_reported",
            "cause-comments": "cause__comments",
            "cause-created": "cause__created",
            "cause-last_updated": "cause__last_updated",
            # effect
            "effect-id": "effect__pk",
            "effect-name": "effect__name",
            "effect-term": "effect__term__name",
            "effect-biological_organization": replace_null("cause__biological_organization__value"),
            "effect-species": "effect__species",
            "effect-units": "effect__units",
            "effect-as_reported": "effect__as_reported",
            "effect-comments": "effect__comments",
            "effect-created": "effect__created",
            "effect-last_updated": "effect__last_updated",
            # result
            "result-id": "pk",
            "result-name": "name",
            "result-sort_order": "sort_order",
            "result-relationship_direction": sql_display(
                "relationship_direction", ChangeTrajectory
            ),
            "result-relationship_comment": "relationship_comment",
            "result-statistical_sig_type": replace_null("statistical_sig_type__value"),
            "result-statistical_sig_value": "statistical_sig_value",
            "result-modifying_factors": "modifying_factors",
            "result-modifying_factors_comment": "modifying_factors_comment",
            "result-measure_type": replace_null("measure_type__value"),
            "result-measure_value": "measure_value",
            "result-derived_value": "derived_value",
            "result-sample_size": "sample_size",
            "result-variability": replace_null("variability__value"),
            "result-low_variability": "low_variability",
            "result-upper_variability": "upper_variability",
            "result-comments": "comments",
            "result-created": "created",
            "result-last_updated": "last_updated",
        }
        qs = self.annotate(
            **study_df_annotations("design__study__"),
            design__countries__name=str_m2m("design__countries__name"),
            design__states__name=str_m2m("design__states__name"),
            design__ecoregions__value=str_m2m("design__ecoregions__value"),
            design__habitats__value=str_m2m("design__habitats__value"),
            design__climates__value=str_m2m("design__climates__value"),
        ).values_list(*list(mapping.values()))
        return pd.DataFrame(data=qs, columns=list(mapping.keys()))


class ResultManager(BaseManager):
    assessment_relation = "design__study__assessment"

    def get_queryset(self):
        return ResultQuerySet(self.model, using=self._db)
