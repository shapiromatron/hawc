import numpy as np
import pandas as pd
from django.db.models import Q

from ..common.exports import ModelExport, clean_html
from ..common.models import sql_display, sql_format, str_m2m
from ..lit.constants import ReferenceDatabase
from .constants import CoiReported


class StudyExport(ModelExport):
    def get_value_map(self):
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

    def get_annotation_map(self, query_prefix):
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
            "url": sql_format("/study/{}/", query_prefix + "pk"),  # hardcoded URL
        }

    def prepare_df(self, df):
        # cast from string to nullable int
        for key in [self.get_column_name("pubmed_id"), self.get_column_name("hero_id")]:
            if key in df.columns:
                df[key] = pd.to_numeric(df[key], errors="coerce")

        # cast from string to null
        doi = self.get_column_name("doi")
        if doi in df.columns:
            df[doi] = df[doi].mask(df[doi] == "", np.nan)

        # clean html text
        summary = self.get_column_name("summary")
        if summary in df.columns:
            df.loc[:, summary] = clean_html(df[summary])
        return df
