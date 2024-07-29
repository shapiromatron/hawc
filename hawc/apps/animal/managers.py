from typing import Any

import numpy as np
import pandas as pd
from django.apps import apps
from django.db import models, transaction
from django.db.models import Case, F, Max, Min, OuterRef, QuerySet, Subquery, Value, When
from django.db.models.functions import Concat
from rest_framework.serializers import ValidationError

from ..assessment.models import Assessment, DoseUnits
from ..common.models import BaseManager, get_distinct_charfield, get_distinct_charfield_opts
from ..vocab.constants import VocabularyTermType
from ..vocab.models import Term
from . import constants


class ExperimentManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_type_choices(self, assessment_id: int):
        types = set(
            self.model.objects.filter(study__assessment_id=assessment_id)
            .values_list("type", flat=True)
            .distinct()
        )
        return [c for c in constants.ExperimentType.choices if c[0] in types]


class AnimalGroupManager(BaseManager):
    assessment_relation = "experiment__study__assessment"

    def animal_description(self, assessment_id: int) -> pd.DataFrame:
        """Returns animal description with and without the number of animals.

        This method mirrors the exports.get_gen_species_strain_sex method, but uses results from
        a database queryset instead of a deeply nested dictionary representation.

        Args:
            assessment_id (int): Assessment id.

        Returns:
            pandas Dataframe of data
        """
        qs = (
            self.filter(experiment__study__assessment_id=assessment_id)
            .annotate(
                min_n=Min("endpoints__groups__n"),
                max_n=Max("endpoints__groups__n"),
            )
            .values_list(
                "id",
                "species__name",
                "strain__name",
                "sex",
                "generation",
                "min_n",
                "max_n",
                "experiment__type",
                "dosing_regime__duration_exposure_text",
            )
        )
        rows = []
        for id, species, strain, sex, generation, min_n, max_n, exp_type, duration_text in qs:
            gen = self.model.get_generation_short(generation)
            if len(gen) > 0:
                gen += " "

            sex = self.model.SEX_SYMBOLS[sex]
            if sex == "NR":
                sex = "sex=NR"

            ns = "N=NR"
            if min_n or max_n:
                ns = f"N={min_n}" if min_n == max_n else f"N={min_n}-{max_n}"

            treatment_text = constants.ExperimentType(exp_type).label
            if "(" in treatment_text:
                treatment_text = treatment_text[: treatment_text.find("(")]

            if duration_text:
                treatment_text += f" ({duration_text})"

            rows.append(
                (
                    id,
                    f"{gen}{species}, {strain} ({sex})",
                    f"{gen}{species}, {strain} ({sex}, {ns})",
                    treatment_text,
                )
            )

        return pd.DataFrame(
            data=rows,
            columns=[
                "animal group id",
                "animal description",
                "animal description, with n",
                "treatment period",
            ],
        )


class DosingRegimeManager(BaseManager):
    assessment_relation = "dosed_animals__experiment__study__assessment"


class DoseGroupManager(BaseManager):
    assessment_relation = "dose_regime__dosed_animals__experiment__study__assessment"

    def by_dose_regime(self, dose_regime):
        return self.filter(dose_regime=dose_regime)


class EndpointQuerySet(QuerySet):
    def annotate_dose_values(self, dose_units: DoseUnits | None = None) -> QuerySet:
        """Annotate dose unit-specific responses from queryset, if a dose-unit is available.

        Args:
            dose_units (Optional[DoseUnits]): selected dose units, if exists
        """
        if dose_units is None:
            return self.annotate(
                units_name=Value("", output_field=models.CharField()),
                noel_value=Value(None, output_field=models.FloatField(null=True)),
                loel_value=Value(None, output_field=models.FloatField(null=True)),
                bmd=Value(None, output_field=models.FloatField(null=True)),
                bmdl=Value(None, output_field=models.FloatField(null=True)),
            )
        DoseGroup = apps.get_model("animal", "DoseGroup")
        noel_value_qs = DoseGroup.objects.filter(
            dose_regime__animalgroup__endpoints=OuterRef("pk"),
            dose_group_id=OuterRef("NOEL"),
            dose_units=dose_units,
        )
        loel_value_qs = DoseGroup.objects.filter(
            dose_regime__animalgroup__endpoints=OuterRef("pk"),
            dose_group_id=OuterRef("LOEL"),
            dose_units=dose_units,
        )
        Session = apps.get_model("bmd", "Session")
        bmd_qs = Session.objects.filter(endpoint=OuterRef("pk"), dose_units=dose_units, active=True)
        return self.annotate(
            units_name=Value(dose_units.name, output_field=models.CharField()),
            noel_value=Subquery(noel_value_qs.values("dose")),
            loel_value=Subquery(loel_value_qs.values("dose")),
            bmd=Subquery(bmd_qs.values("selected__bmd")),
            bmdl=Subquery(bmd_qs.values("selected__bmdl")),
        )

    def selector(self) -> QuerySet:
        """Get a queryset of endpoints with a label for use in an assessment-level selector."""
        return (
            self.annotate(
                label=Concat(
                    F("animal_group__experiment__study__short_citation"),
                    Case(
                        When(
                            animal_group__experiment__study__published=False,
                            then=Value(" (unpublished)"),
                        ),
                        default=Value(""),
                    ),
                    Value(" | "),
                    F("animal_group__experiment__name"),
                    Value(" | "),
                    F("animal_group__name"),
                    Value(" | "),
                    F("name"),
                )
            )
            .order_by(
                "animal_group__experiment__study__short_citation",
                "animal_group__experiment__name",
                "animal_group__name",
                "name",
            )
            .only("id")  # https://code.djangoproject.com/ticket/30052
        )

    def published_only(self, published_only=True):
        return (
            self.filter(animal_group__experiment__study__published=True) if published_only else self
        )


class EndpointManager(BaseManager):
    assessment_relation = "assessment"

    def get_queryset(self):
        return EndpointQuerySet(self.model, using=self._db)

    def optimized_qs(self, **filters):
        return (
            self.filter(**filters)
            .select_related(
                "animal_group",
                "animal_group__dosed_animals",
                "animal_group__experiment",
                "animal_group__experiment__study",
            )
            .prefetch_related(
                "groups",
                "effects",
                "animal_group__dosed_animals__doses",
            )
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

    def endpoint_df(self, assessment: Assessment, published_only: bool) -> pd.DataFrame:
        filters: dict[str, Any] = {"assessment_id": assessment}
        if published_only:
            filters["animal_group__experiment__study__published"] = True

        DoseGroup = apps.get_model("animal", "DoseGroup")
        Endpoint = apps.get_model("animal", "Endpoint")
        Session = apps.get_model("bmd", "Session")

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
            name="endpoint name",
            system="system",
            organ="organ",
            effect="effect",
            effect_subtype="effect subtype",
            NOEL="noel",
            LOEL="loel",
            FEL="fel",
        )
        qs = Endpoint.objects.filter(**filters).values_list(*values.keys()).order_by("id")
        df1 = pd.DataFrame(data=qs, columns=values.values())

        # get BMD values
        values = dict(
            endpoint_id="endpoint id",
            dose_units_id="dose units id",
            selected__bmd="bmd",
            selected__bmdl="bmdl",
        )
        qs = Session.objects.filter(endpoint__assessment=assessment, active=True).values_list(
            *values.keys()
        )
        df2 = (
            pd.DataFrame(data=qs, columns=values.values())
            .dropna()
            .set_index(["endpoint id", "dose units id"])
        )

        # get dose regime values
        filters = dict(dose_regime__dosed_animals__experiment__study__assessment=assessment)
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
                how="left",
                left_index=True,
                right_index=True,
            )
            .set_index("dose units id", append=True)
        )

        # fetch all the dose units tested
        doses = (
            df3.sort_values("dose_group_id")
            .groupby(["dose regime id", "dose units id"])
            .agg(
                dict(
                    dose=lambda els: ", ".join(
                        str(int(el)) if el.is_integer() else str(el) for el in els
                    )
                )
            )
            .rename(columns=dict(dose="doses"))[["doses"]]
        )
        df4 = df4.merge(doses, how="left", left_index=True, right_index=True)

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
                "endpoint name",
                "system",
                "organ",
                "effect",
                "effect subtype",
                "doses",
                "noel",
                "loel",
                "fel",
                "bmd",
                "bmdl",
            ]
        ]

    def migrate_terms(self, assessment: Assessment) -> pd.DataFrame:
        """
        Update all endpoints in assessment to try to match fields to controlled vocabulary. Use
        a case-insensitive match.
        """

        # Term type to text field
        type_to_text_field = VocabularyTermType.value_to_text_field()
        # Term type to term field
        type_to_term_field = VocabularyTermType.value_to_term_field()

        # Ordered types
        types = sorted(list(type_to_term_field.keys()))

        # Assessment endpoints
        updated_endpoints = []

        # List of endpoint terms dicts; will be used to generate excel report
        endpoint_export_columns = {
            "id": "endpoint id",
            "system": "system",
            "organ": "organ",
            "effect": "effect",
            "effect_subtype": "effect_subtype",
            "name": "endpoint name",
            "system_term_id": "system_term_id",
            "organ_term_id": "organ_term_id",
            "effect_term_id": "effect_term_id",
            "effect_subtype_term_id": "effect_subtype_term_id",
            "name_term_id": "name_term_id",
        }
        endpoint_export_data = []

        # build parent_id dictionary; we set system where parent_id is None to -1
        terms_dict = {
            (term[0], term[1] or -1, term[2].lower()): term[3]
            for term in Term.objects.filter(namespace=assessment.vocabulary).values_list(
                "type", "parent_id", "name", "id"
            )
        }

        for endpoint in self.assessment_qs(assessment.id).iterator():
            # Check system -> organ -> effect -> effect_subtype -> endpoint_name
            parent_id = -1  # last term parent id; -1 is special-case for system
            for term_type_id in types:
                text_field = type_to_text_field[term_type_id]
                key = (term_type_id, parent_id, getattr(endpoint, text_field).lower())
                match_id = terms_dict.get(key)
                if match_id:
                    setattr(endpoint, type_to_term_field[term_type_id], match_id)
                parent_id = match_id

            # If changed, add to the update list
            if parent_id != -1:
                updated_endpoints.append(endpoint)

            # always update report
            endpoint_export_data.append(
                [getattr(endpoint, col) for col in endpoint_export_columns.keys()]
            )

        # update endpoints
        self.bulk_update(updated_endpoints, list(type_to_term_field.values()))

        # create data frame report
        df = pd.DataFrame(
            data=endpoint_export_data,
            columns=list(endpoint_export_columns.values()),
        )

        return df

    def _validate_update_terms(self, objs: list[dict], assessment: Assessment):
        # assessment must have vocab
        if assessment.vocabulary is None:
            raise ValidationError("Vocabulary not set in assessment {assessment.id}")
        # must be 1 or more objs
        if len(objs) == 0:
            raise ValidationError("List of endpoints must be > 1")
        # each obj must be a dict of endpoint id and name_term_id
        for obj in objs:
            keys = set(obj.keys())
            if keys != {"id", "name_term_id"}:
                raise ValidationError(
                    f"Expected endpoint keys are id and name_term_id; received key(s) {' ,'.join(keys)}"
                )
        # ids must be unique
        endpoint_ids = [obj["id"] for obj in objs]
        if len(endpoint_ids) != len(set(endpoint_ids)):
            raise ValidationError("Endpoint ids must be unique")
        # ids must be valid
        endpoints = self.get_queryset().filter(pk__in=endpoint_ids)
        valid_endpoint_ids = endpoints.values_list("id", flat=True)
        invalid_endpoint_ids = set(endpoint_ids) - set(valid_endpoint_ids)
        if len(invalid_endpoint_ids) > 0:
            invalid_endpoint_ids_str = ", ".join(str(_) for _ in invalid_endpoint_ids)
            raise ValidationError(f"Invalid endpoint id(s) {invalid_endpoint_ids_str}")
        # endpoints must be in the same assessment
        excluded_endpoints = endpoints.exclude(assessment_id=assessment.id)
        if excluded_endpoints.exists():
            excluded_endpoints_str = ", ".join(str(_.pk) for _ in excluded_endpoints)
            raise ValidationError(
                f"Endpoints must be from the same assessment; endpoint id(s) {excluded_endpoints_str} not from assessment id {assessment.id}"
            )
        # term ids must be valid
        term_ids = {obj["name_term_id"] for obj in objs}
        terms = Term.objects.filter(pk__in=term_ids)
        valid_term_ids = terms.values_list("id", flat=True)
        invalid_term_ids = term_ids - set(valid_term_ids)
        if len(invalid_term_ids) > 0:
            invalid_term_ids_str = ", ".join(str(_) for _ in invalid_term_ids)
            raise ValidationError(f"Invalid term id(s) {invalid_term_ids_str}")
        # terms must be in the correct vocabulary
        excluded_terms = terms.exclude(namespace=assessment.vocabulary)
        if excluded_terms.exists():
            excluded_terms_str = ", ".join(str(_.pk) for _ in excluded_terms)
            raise ValidationError(
                f"Term id(s) {excluded_terms_str} are not in the assessment vocabulary"
            )
        # terms must be the correct type
        excluded_terms = terms.exclude(type=VocabularyTermType.endpoint_name)
        if excluded_terms.exists():
            excluded_terms_str = ", ".join(str(_.pk) for _ in excluded_terms)
            raise ValidationError(f"Term id(s) {excluded_terms_str} are not type endpoint_name")

    @transaction.atomic
    def update_terms(self, objs: list[dict], assessment: Assessment) -> list:
        """
        Updates all of the terms and respective text fields
        for a list of endpoints based on the given name term.
        All endpoints must be from the same assessment.

        Args:
            objs (list[dict]): List of endpoint dicts, where each dict has
                for keys 'id' and 'name_term_id'
            assessment (Assessment): Assessment for endpoints

        Returns:
            list: Updated endpoints
        """
        # validate the endpoints and terms
        self._validate_update_terms(objs, assessment)

        # map endpoints to their name terms
        endpoint_id_to_term_id = {obj["id"]: obj["name_term_id"] for obj in objs}

        # set endpoint terms
        terms_df = Term.vocab_dataframe(assessment.vocabulary)
        endpoint_ids = [obj["id"] for obj in objs]
        endpoints = self.get_queryset().filter(pk__in=endpoint_ids)
        type_to_text_field = VocabularyTermType.value_to_text_field()
        type_to_term_field = VocabularyTermType.value_to_term_field()
        updated_endpoints = []
        updated_fields = list(type_to_text_field.values()) + list(type_to_term_field.values())
        for endpoint in endpoints:
            term_id = endpoint_id_to_term_id[endpoint.id]
            terms_row = terms_df.loc[terms_df["name_term_id"] == term_id].iloc[0]
            for field in updated_fields:
                setattr(endpoint, field, terms_row[field])
            updated_endpoints.append(endpoint)

        self.bulk_update(updated_endpoints, updated_fields)

        return updated_endpoints


class EndpointGroupManager(BaseManager):
    assessment_relation = "endpoint__assessment"
