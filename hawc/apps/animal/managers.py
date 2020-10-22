from typing import Any, Dict, List

import numpy as np
import pandas as pd
from django.apps import apps
from rest_framework.serializers import ValidationError

from ..assessment.models import Assessment
from ..common.models import BaseManager, get_distinct_charfield, get_distinct_charfield_opts
from ..vocab.models import Term, VocabularyTermType


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

    def endpoint_df(self, assessment: Assessment, published_only: bool) -> pd.DataFrame:
        filters: Dict[str, Any] = {"assessment_id": assessment}
        if published_only:
            filters["animal_group__experiment__study__published"] = True

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
            model__output__BMD="BMD",
            model__output__BMDL="BMDL",
            model__session__dose_units_id="dose units id",
        )
        qs = SelectedModel.objects.filter(endpoint__assessment=assessment).values_list(
            *values.keys()
        )
        df2 = (
            pd.DataFrame(data=qs, columns=values.values())
            .dropna()
            .set_index(["endpoint id", "dose units id"])
            .rename(columns=dict(BMD="bmd", BMDL="bmdl"))
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
        # Type integer to type name
        term_types = VocabularyTermType.as_dict()

        # Type name to common attr name
        term_type_to_text_field = {
            "system": "system",
            "organ": "organ",
            "effect": "effect",
            "effect_subtype": "effect_subtype",
            "endpoint_name": "name",
        }
        # Common attr name to term attr name
        text_to_term_field = {
            "system": "system_term_id",
            "organ": "organ_term_id",
            "effect": "effect_term_id",
            "effect_subtype": "effect_subtype_term_id",
            "name": "name_term_id",
        }

        # Type integers, ordered.
        types = sorted(list(term_types.keys()))

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
                text_field = term_type_to_text_field[term_types[term_type_id]]
                key = (term_type_id, parent_id, getattr(endpoint, text_field).lower())
                match_id = terms_dict.get(key)
                if match_id:
                    setattr(endpoint, text_to_term_field[text_field], match_id)
                parent_id = match_id

            # If changed, add to the update list
            if parent_id != -1:
                updated_endpoints.append(endpoint)

            # always update report
            endpoint_export_data.append(
                [getattr(endpoint, col) for col in endpoint_export_columns.keys()]
            )

        # update endpoints
        self.bulk_update(updated_endpoints, list(text_to_term_field.values()))

        # create data frame report
        df = pd.DataFrame(
            data=endpoint_export_data, columns=list(endpoint_export_columns.values()),
        )

        return df

    def update_terms(self, objs: List[Dict]) -> List:
        # must be 1 or more objs
        if len(objs) == 0:
            raise ValidationError("List of endpoints must be > 1")
        # each obj must have id and at least one other field
        for obj in objs:
            if "id" not in obj.keys():
                raise ValidationError("Each endpoint must have an 'id'")
            if len(obj.keys()) < 2:
                raise ValidationError(f"No term fields given for endpoint {obj['id']}")

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
            raise ValidationError(f"Invalid id(s) {invalid_endpoint_ids_str}")
        # endpoints must be in the same assessment
        assessment = endpoints.first().assessment
        invalid_endpoints = endpoints.exclude(assessment_id=assessment.id)
        if invalid_endpoints.exists():
            invalid_endpoints_str = ", ".join(str(_.pk) for _ in invalid_endpoints)
            raise ValidationError(
                f"Endpoints must be from the same assessment; endpoint(s) {invalid_endpoints_str} not from assessment {assessment.id}"
            )
        # assessment must have vocab
        if assessment.vocabulary is None:
            raise ValidationError("Vocabulary not set in assessment {assessment.id}")
        # restructure dict for easier seperation of id and terms
        endpoint_id_to_terms = {obj.pop("id"): obj for obj in objs}
        # obj fields must be terms
        term_fields = {
            "system_term_id",
            "organ_term_id",
            "effect_term_id",
            "effect_subtype_term_id",
            "name_term_id",
        }
        for term_field_to_id in endpoint_id_to_terms.values():
            if not set(term_field_to_id.keys()).issubset(term_fields):
                invalid_fields_str = ", ".join(set(term_field_to_id.keys()) - term_fields)
                raise ValidationError(f"Invalid field name(s) '{invalid_fields_str}'")
        # all terms must be in assessment vocabulary
        term_fields_and_ids = {
            term_field_and_id
            for term_field_to_id in endpoint_id_to_terms.values()
            for term_field_and_id in term_field_to_id.items()
        }
        term_ids = [id for (_, id) in term_fields_and_ids]
        terms = Term.objects.filter(pk__in=term_ids)
        for term in terms:
            if term.namespace != assessment.vocabulary:
                raise ValidationError(
                    f"Assessment vocabulary {assessment.vocabulary} does not match term {term.id} namespace {term.namespace}"
                )
        # all terms must match assigned type
        term_types = VocabularyTermType.as_dict()
        term_type_to_field = {
            "system": "system_term_id",
            "organ": "organ_term_id",
            "effect": "effect_term_id",
            "effect_subtype": "effect_subtype_term_id",
            "endpoint_name": "name_term_id",
        }
        term_field_to_text_field = {
            "system_term_id": "system",
            "organ_term_id": "organ",
            "effect_term_id": "effect",
            "effect_subtype_term_id": "effect_subtype",
            "name_term_id": "name",
        }
        actual_term_fields_and_ids = {
            (term_type_to_field[term_types[term.type]], term.pk) for term in terms
        }
        for term_field_and_id in term_fields_and_ids:
            if term_field_and_id not in actual_term_fields_and_ids:
                field, id = term_field_and_id
                raise ValidationError(f"Term {id} is not the right type for '{field}''")
        # update endpoints
        term_id_to_name = {term.pk: term.name for term in terms}
        updated_endpoints = []
        updated_fields = list(term_field_to_text_field.keys()) + list(
            term_field_to_text_field.values()
        )
        for endpoint in endpoints:
            endpoint_terms = endpoint_id_to_terms[endpoint.pk]
            for field, id in endpoint_terms.items():
                setattr(endpoint, field, id)
                setattr(endpoint, term_field_to_text_field[field], term_id_to_name[id])
            updated_endpoints.append(endpoint)
        self.bulk_update(updated_endpoints, updated_fields)

        return updated_endpoints


class EndpointGroupManager(BaseManager):
    assessment_relation = "endpoint__assessment"
