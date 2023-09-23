import numpy as np
import pandas as pd
from django.db.models import Q

from ..common.exports import Module
from ..common.models import sql_display, sql_format, str_m2m
from ..lit.constants import ReferenceDatabase
from .constants import CoiReported


class StudyModule(Module):
    def _get_value_map(self):
        return {
            "id": "id",
            "hero_id": "hero",
            "pubmed_id": "pmid",
            "doi": "doi",
            "url": "url",
            "short_citation": "short_citation",
            "full_citation": "full_citation",
            "coi_reported": "coi_reported_display",
            "coi_details": "coi_details",
            "funding_source": "funding_source",
            "bioassay": "bioassay",
            "epi": "epi",
            "epi_meta": "epi_meta",
            "in_vitro": "in_vitro",
            "eco": "eco",
            "study_identifier": "study_identifier",
            "contact_author": "contact_author",
            "ask_author": "ask_author",
            "summary": "summary",
            "editable": "editable",
            "published": "published",
        }

    def _get_annotation_map(self, query_prefix):
        return {
            "pmid": str_m2m(
                query_prefix + "identifiers__unique_id",
                filter=Q(**{query_prefix + "identifiers__database": ReferenceDatabase.PUBMED}),
            ),
            "hero": str_m2m(
                query_prefix + "identifiers__unique_id",
                filter=Q(**{query_prefix + "identifiers__database": ReferenceDatabase.HERO}),
            ),
            "doi": str_m2m(
                query_prefix + "identifiers__unique_id",
                filter=Q(**{query_prefix + "identifiers__database": ReferenceDatabase.DOI}),
            ),
            "coi_reported_display": sql_display(query_prefix + "coi_reported", CoiReported),
            "url": sql_format("/study/{}/", query_prefix + "pk"),
        }

    def prepare_df(self, df):
        for key in [f"{self.key_prefix}pubmed_id", f"{self.key_prefix}hero_id"]:
            df[key] = pd.to_numeric(df[key], errors="coerce")
        for key in [f"{self.key_prefix}doi"]:
            df[key] = df[key].replace("", np.nan)
        return df
