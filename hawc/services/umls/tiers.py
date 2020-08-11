import os

import pandas as pd

from . import utils


class TuiFilters:
    # fmt: off
    tuis_1 = {
        "T053", "T054", "T055", "T017", "T018", "T021", "T022", "T023", "T024", "T025", "T026",
        "T029", "T030", "T031", "T109", "T114", "T116", "T121", "T123", "T125", "T126", "T127",
        "T129", "T131", "T192", "T196", "T079", "T080", "T081", "T082", "T102", "T169", "T185",
        "T034", "T038", "T032", "T039", "T040", "T041", "T042", "T043", "T044", "T045", "T201",
        "T019", "T020", "T033", "T037", "T046", "T047", "T048", "T049", "T050", "T184", "T190",
        "T191",
    }
    tuis_2 = {
        "T053", "T054", "T055", "T017", "T018", "T021", "T022", "T023", "T024", "T025", "T026",
        "T029", "T030", "T031", "T109", "T114", "T116", "T121", "T123", "T125", "T126", "T127",
        "T129", "T131", "T192", "T196", "T079", "T080", "T081", "T082", "T102", "T169", "T185",
        "T034", "T038", "T032", "T039", "T040", "T041", "T042", "T043", "T044", "T045", "T201",
        "T019", "T020", "T033", "T037", "T046", "T047", "T048", "T049", "T050", "T184", "T190",
        "T191",
    }
    tuis_3 = {
        "T059", "T053", "T054", "T055", "T017", "T018", "T021", "T022", "T023", "T024", "T025",
        "T026", "T029", "T030", "T031", "T109", "T114", "T116", "T121", "T123", "T125", "T126",
        "T127", "T129", "T131", "T192", "T196", "T079", "T080", "T081", "T082", "T102", "T169",
        "T185", "T034", "T038", "T032", "T039", "T040", "T041", "T042", "T043", "T044", "T045",
        "T201", "T019", "T020", "T033", "T037", "T046", "T047", "T048", "T049", "T050", "T184",
        "T190", "T191",
    }
    tuis_6 = {
        "T053", "T054", "T055", "T017", "T018", "T021", "T022", "T023", "T024", "T025", "T026",
        "T029", "T030", "T031", "T109", "T114", "T116", "T121", "T123", "T125", "T126", "T127",
        "T129", "T131", "T192", "T196", "T079", "T080", "T081", "T082", "T102", "T169", "T185",
        "T034", "T038", "T032", "T039", "T040", "T041", "T042", "T043", "T044", "T045", "T201",
        "T019", "T020", "T033", "T037", "T046", "T047", "T048", "T049", "T050", "T184", "T190",
        "T191",
    }
    tuis = {
        "T053", "T054", "T055", "T017", "T018", "T021", "T022", "T023", "T024", "T025", "T026",
        "T029", "T030", "T031", "T109", "T114", "T116", "T121", "T123", "T125", "T126", "T127",
        "T129", "T131", "T192", "T196", "T079", "T080", "T081", "T082", "T102", "T169", "T185",
        "T034", "T038", "T032", "T039", "T040", "T041", "T042", "T043", "T044", "T045", "T201",
        "T019", "T020", "T033", "T037", "T046", "T047", "T048", "T049", "T050", "T184", "T190",
        "T191",
    }
    # fmt: on


def run_tier(series: pd.Series, max_results: int = None, confidence: float = None, tuis=None):
    linker, nlp = utils.loadUMLSLinker(max_results, confidence)
    return zip(
        *series.apply(
            utils.breakIntoSpansAndUMLS,
            tuiFilter=tuis,
            RequireNonObsoleteDef=True,
            nlp=nlp,
            linker=linker,
        )
    )


def run_tiered_analysis(df: pd.DataFrame, series_name: str, umls_apikey: str) -> pd.DataFrame:
    series = df[series_name]
    df["endpoint-name_Tier1"], df["endpoint-name_Tier1-Count"] = run_tier(
        series, 999, 0.98, TuiFilters.tuis_1
    )
    df["endpoint-name_Tier2"], df["endpoint-name_Tier2-Count"] = run_tier(
        series, 999, 0.85, TuiFilters.tuis_2
    )
    df["endpoint-name_Tier3"], df["endpoint-name_Tier3-Count"] = run_tier(
        series, 999, 0.5, TuiFilters.tuis_3
    )
    df["endpoint-name_Tier4"], df["endpoint-name_Tier4-Count"] = run_tier(series, 999, 0.5, None)

    df["endpoint-name_Tier5_REST"] = series.apply(utils.UMLS_RestLookup, apikey=umls_apikey)
    df["endpoint-name_Tier5_REST_CLEANED"] = df["endpoint-name_Tier5_REST"].apply(
        utils.REST_JSON_to_Read
    )

    linker, nlp = utils.loadUMLSLinker(999, 0.85)
    df["endpoint-name_Tier6_EntityBreaking"], df["endpoint-name_Tier6-Count"] = zip(
        *series.apply(
            utils.breakIntoEntitiesAndUMLS, tuiFilter=TuiFilters.tuis_6, nlp=nlp, linker=linker
        )
    )

    return df


def main() -> pd.DataFrame:
    umls_apikey = os.environ['UMLS_API_KEY']
    df = pd.read_excel("HAWC_Ontologies_14November2019.xlsx", sheet_name="Endpoints", usecols="A:C")

    # organ
    df["endpoint-organ_UMLS"], df["endpoint-organ_UMLS_Count"] = run_tier(
        df["endpoint-organ"], 999, 0.5, TuiFilters.tuis
    )

    # system
    df["endpoint-system_UMLS"], df["endpoint-system_UMLS_Count"] = run_tier(
        df["endpoint-system"], 999, 0.5, TuiFilters.tuis
    )

    df["endpoint-name-flipped"] = df["endpoint-name"].apply(utils.flipOnComma)
    df = run_tiered_analysis(df, "endpoint-name-flipped", umls_apikey)

    return df
