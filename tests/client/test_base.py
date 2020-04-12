import pandas as pd

from hawc_client import BaseClient


def test_csv_to_df():
    client = BaseClient(None)
    csv = "column1,column2,column3\na,b,c\n1,2,3"
    df = pd.DataFrame(data={"column1": ["a", "1"], "column2": ["b", "2"], "column3": ["c", "3"]})
    assert client._csv_to_df(csv).equals(df)
