import pandas as pd
from django.apps import apps

from ...common.helper import create_uuid
from ...lit import constants


def bioassay_ml_dataset() -> pd.DataFrame:
    Endpoint = apps.get_model("animal", "Endpoint")
    # map of django field names to friendlier column names
    column_map = {
        "assessment_id": "assessment_uuid",
        "name": "endpoint_name",
        "animal_group__experiment__chemical": "chemical",
        "animal_group__species__name": "species",
        "animal_group__strain__name": "strain",
        "animal_group__sex": "sex",
        "system": "endpoint_system",
        "organ": "endpoint_organ",
        "effect": "endpoint_effect",
        "effect_subtype": "endpoint_effect_subtype",
        "data_location": "endpoint_data_location",
        "animal_group__experiment__study__title": "study_title",
        "animal_group__experiment__study__abstract": "study_abstract",
        "animal_group__experiment__study__full_citation": "study_full_citation",
        "animal_group__experiment__study__identifiers__database": "db",
        "animal_group__experiment__study__identifiers__unique_id": "db_id",
    }
    queryset = (
        Endpoint.objects.filter(assessment__is_public_training_data=True)
        .select_related(
            "animal_group",
            "animal_group__species",
            "animal_group__strain",
            "animal_group__experiment",
            "animal_group__experiment__study",
            "animal_group__experiment__study__identifiers",
        )
        .values(*column_map.keys())
    )

    df = pd.DataFrame.from_records(queryset).rename(
        columns={k: v for k, v in column_map.items() if v is not None}
    )

    # Creates a UUID for each assessment_id, providing anonymity
    df["assessment_uuid"] = df["assessment_uuid"].apply(create_uuid)

    # Assigns db_id to hero_id in all instances where db == HERO
    df["hero_id"] = None
    df.loc[df["db"] == constants.HERO, ["hero_id"]] = df["db_id"][df["db"] == constants.HERO]

    # Assigns db_id to pubmed_id in all instances where db == PUBMED
    df["pubmed_id"] = None
    df.loc[df["db"] == constants.PUBMED, ["pubmed_id"]] = df["db_id"][df["db"] == constants.PUBMED]

    df = df.drop(columns=["db", "db_id"]).drop_duplicates()

    return df
