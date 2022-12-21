import pandas as pd
from rapidfuzz import process


def fuzz_match(
    src_df: pd.DataFrame,
    dst_df: pd.DataFrame,
    src_match_column: str,
    dst_match_column: str,
    dst_key_column: str,
    match_prefix="matched",
) -> pd.DataFrame:
    """Returns a copy of the source dataframe with a matching key value in destination.

    Args:
        src_df (pd.DataFrame): The source dataframe
        dst_df (pd.DataFrame): The matching dataframe
        src_match_column (str): The column name to attempt to match in the source
        dst_match_column (str): The column name to match to in the destination
        dst_key_column (str): The key value to return for a match
        match_prefix (str, optional): Prefix for new columns; to "matched".

    Returns:
        pd.DataFrame: _description_
    """
    comparitor = dst_df[dst_match_column].values

    def func(row):
        # returns (text, score, index)
        return process.extractOne(row[src_match_column], comparitor)

    applied_df = src_df.apply(func, axis="columns", result_type="expand")
    applied_df.loc[:, 3] = dst_df.iloc[applied_df[2].values][dst_key_column].values
    applied_df = applied_df[[3, 1, 0]].rename(
        columns={3: f"{match_prefix}_key", 1: f"{match_prefix}_score", 0: f"{match_prefix}_text"}
    )
    return pd.concat([src_df, applied_df], axis="columns")
