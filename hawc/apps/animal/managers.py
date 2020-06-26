import numpy as np
import pandas as pd
from django.apps import apps

from ..common.models import BaseManager, get_distinct_charfield, get_distinct_charfield_opts


class ExperimentManager(BaseManager):
    assessment_relation = "study__assessment"


class AnimalGroupManager(BaseManager):
    assessment_relation = "experiment__study__assessment"


class DosingRegimeManager(BaseManager):
    assessment_relation = "dosed_animals__experiment__study__assessment"


class DoseGroupManager(BaseManager):
    assessment_relation = "dose_regime__dosed_animals__experiment__study__assessment"

    def by_dose_regime(self, dose_regime):
        return self.filter(dose_regime=dose_regime)


class EndpointManager(BaseManager):
    assessment_relation = "assessment"

    def published(self, assessment_id=None):
        return self.get_qs(assessment_id).filter(animal_group__experiment__study__published=True)

    def tag_qs(self, assessment_id, tag_slug=None):
        AnimalGroup = apps.get_model("animal", "AnimalGroup")
        Experiment = apps.get_model("animal", "Experiment")
        Study = apps.get_model("study", "Study")
        return (
            self.filter(effects__slug=tag_slug)
            .select_related("animal_group", "animal_group__dosing_regime")
            .prefetch_related("animal_group__dosing_regime__doses")
            .filter(
                animal_group__in=AnimalGroup.objects.filter(
                    experiment__in=Experiment.objects.filter(
                        study__in=Study.objects.get_qs(assessment_id)
                    )
                )
            )
        )

    def optimized_qs(self, **filters):
        return (
            self.filter(**filters)
            .select_related(
                "animal_group",
                "animal_group__dosed_animals",
                "animal_group__experiment",
                "animal_group__experiment__study",
            )
            .prefetch_related("groups", "effects", "animal_group__dosed_animals__doses",)
        )

    def get_system_choices(self, assessment_id):
        return get_distinct_charfield_opts(self, assessment_id, "system")

    def get_organ_choices(self, assessment_id):
        return get_distinct_charfield_opts(self, assessment_id, "organ")

    def get_effect_choices(self, assessment_id):
        return get_distinct_charfield_opts(self, assessment_id, "effect")

    def get_effect_subtype_choices(self, assessment_id):
        return get_distinct_charfield_opts(self, assessment_id, "effect_subtype")

    def get_effects(self, assessment_id):
        return get_distinct_charfield(self, assessment_id, "effect")

    def endpoint_df(self, assessment_id: int) -> pd.DataFrame:
        # TODO - add published/unpublished check
        DoseGroup = apps.get_model("animal", "DoseGroup")
        Endpoint = apps.get_model("animal", "Endpoint")
        SelectedModel = apps.get_model("bmd", "SelectedModel")

        # get endpoint level data
        values = dict(
            animal_group__experiment__study__id="study id",
            animal_group__experiment__study__short_citation="study citation",
            animal_group__experiment_id="experiment id",
            animal_group__experiment__name="experiment name",
            animal_group__id="animal group id",
            animal_group__name="animal group name",
            animal_group__dosing_regime_id="dose regime id",
            id="endpoint id",
            NOEL="noel",
            LOEL="loel",
            FEL="fel",
        )
        qs = Endpoint.objects.filter(
            animal_group__experiment__study__assessment_id=assessment_id
        ).values_list(*values.keys())
        df1 = pd.DataFrame(data=qs, columns=values.values())

        # get BMD values
        values = dict(
            endpoint_id="endpoint id",
            model__output__BMD="BMD",
            model__output__BMDL="BMDL",
            model__session__dose_units_id="dose units id",
        )
        qs = SelectedModel.objects.filter(endpoint__assessment_id=assessment_id).values_list(
            *values.keys()
        )
        df2 = (
            pd.DataFrame(data=qs, columns=values.values())
            .dropna()
            .set_index(["endpoint id", "dose units id"])
            .rename(columns=dict(BMD="bmd", BMDL="bmdl"))
        )

        # get dose regime values
        filters = dict(dose_regime__dosed_animals__experiment__study__assessment_id=assessment_id)
        values = dict(
            dose_regime_id="dose regime id",
            dose_units_id="dose units id",
            dose_units__name="dose units name",
            dose_group_id="dose_group_id",
            dose="dose",
        )
        qs = DoseGroup.objects.filter(**filters).values_list(*values.keys())
        df3 = pd.DataFrame(data=qs, columns=values.values())

        # merge dose units and endpoint id
        subset = df3[["dose regime id", "dose units id", "dose units name"]].drop_duplicates()
        df4 = (
            df1.set_index("dose regime id")
            .merge(
                subset.set_index("dose regime id")[["dose units name", "dose units id"]],
                left_index=True,
                right_index=True,
            )
            .set_index("dose units id", append=True)
        )

        # fetch all the dose units tested
        df4["doses"] = (
            df3.sort_values("dose_group_id")
            .groupby(["dose regime id", "dose units id"])
            .agg(
                dict(
                    dose=lambda els: ", ".join(
                        str(int(el)) if el.is_integer() else str(el) for el in els
                    )
                )
            )
            .dose
        )

        # replace {NOEL, LOEL, FEL} dose group index with values
        def get_doses(r, col):
            el = r[col]
            if el == -999:
                return np.NaN
            try:
                return df3.loc[(r["dose regime id"], r["dose units id"], el), "dose"]
            except KeyError:
                return np.NaN

        df3 = df3.reset_index().set_index(["dose regime id", "dose units id", "dose_group_id"])

        df4 = df4.reset_index()
        df4.loc[:, "noel"] = df4.apply(get_doses, axis=1, args=("noel",))
        df4.loc[:, "loel"] = df4.apply(get_doses, axis=1, args=("loel",))
        df4.loc[:, "fel"] = df4.apply(get_doses, axis=1, args=("fel",))
        df4 = df4.drop(columns="dose regime id").set_index(["endpoint id", "dose units id"])

        # merge everything together
        df5 = df4.merge(df2, how="left", left_index=True, right_index=True).reset_index()
        return df5[
            [
                "study id",
                "study citation",
                "experiment id",
                "experiment name",
                "animal group id",
                "animal group name",
                "dose units id",
                "dose units name",
                "endpoint id",
                "doses",
                "noel",
                "loel",
                "fel",
                "bmd",
                "bmdl",
            ]
        ]


class EndpointGroupManager(BaseManager):
    assessment_relation = "endpoint__assessment"
