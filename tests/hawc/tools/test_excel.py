from io import BytesIO

import pandas as pd
from openpyxl import load_workbook

from hawc.tools.excel import format_worksheet, get_writer, write_worksheet


def write_and_load(df: pd.DataFrame, **kwargs):
    # write dataframe to excel file with data tab, then load the excel workbook and return a worksheet
    f, writer = get_writer()
    write_worksheet(writer, "data", df, **kwargs)
    writer.close()
    return load_workbook(BytesIO(f.getvalue()))["data"]


class TestWriteWorksheet:
    def test_format(self):
        ws = write_and_load(pd.DataFrame({"a": [1], "b": ["x"]}))
        assert ws.freeze_panes == "A2"
        assert ws.auto_filter.ref == "A1:B2"
        assert ws["A1"].fill.fgColor.rgb.endswith("1F497D")
        assert ws.column_dimensions["A"].width == 10

    def test_no_format(self):
        ws = write_and_load(pd.DataFrame({"a": [1]}), format=False)
        assert ws.auto_filter.ref is None

    def test_timezone_removed(self):
        df = pd.DataFrame({"d": pd.to_datetime(["2024-01-02 03:04:05"]).tz_localize("UTC")})
        ws = write_and_load(df)
        assert ws["A2"].value.isoformat() == "2024-01-02T03:04:05"

    def test_illegal_characters_string_column(self):
        ws = write_and_load(pd.DataFrame({"a": ["a\x02b"]}))
        assert ws["A2"].value == "ab"

    def test_illegal_characters_object_column(self):
        # object dtype column (e.g. mixed values) holding a string with an illegal character
        df = pd.DataFrame({"a": pd.Series(["c\x03d"], dtype=object)})
        ws = write_and_load(df)
        assert ws["A2"].value == "cd"

    def test_illegal_characters_non_string_object(self):
        # object columns without string accessor are left untouched when cleaning
        df = pd.DataFrame({"s": ["a\x02b"], "n": pd.Series([1], dtype=object)})
        df["n"] = df["n"].astype(int)
        ws = write_and_load(df)
        assert ws["A2"].value == "ab"
        assert ws["B2"].value == 1


def test_format_worksheet():
    ws = write_and_load(pd.DataFrame({"a": [1]}), format=False)
    format_worksheet(ws)
    assert ws["A1"].font.color.rgb.endswith("FFFFFF")
