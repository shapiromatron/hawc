import pandas as pd
from rapidfuzz import process


def fuzz_match(
    src_df: pd.DataFrame,
    dest_df: pd.DataFrame,
    key_src: str,
    key_dest: str,
    match_key: str,
    match_prefix="fuzz",
) -> pd.DataFrame:
    """Returns a copy of the source dataframe with a matching key value in destination.

    Args:
        src_df (pd.DataFrame): The source dataframe
        dest_df (pd.DataFrame): The matching dataframe
        key_src (str): The column name to attempt to match in the source
        key_dest (str): The column name to match to in the destination
        match_key (str): The key value to return for a match
        match_prefix (str, optional): Prefix for new columns; to "fuzz"

    Returns:
        pd.DataFrame: _description_
    """
    comparitor = dest_df[key_dest].values

    def func(row):
        # returns (text, score, index)
        return process.extractOne(row[key_src], comparitor)

    applied_df = src_df.apply(func, axis="columns", result_type="expand")
    applied_df.loc[:, 3] = dest_df.iloc[applied_df[2].values][match_key].values
    applied_df = applied_df[[3, 1, 0]].rename(
        columns={3: f"{match_prefix}_key", 1: f"{match_prefix}_score", 0: f"{match_prefix}_text"}
    )
    return pd.concat([src_df, applied_df], axis="columns")
