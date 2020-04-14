import pandas as pd


class FlatExporter(object):
    """
    Base class used to generate flat-file exports of serialized data.
    """

    def __init__(self, queryset, export_format=None):
        self.queryset = queryset
        self.export_format = export_format

    @classmethod
    def _get_tags(cls, e):
        returnValue = ""

        if "effects" in e:
            """ This element is an Outcome element with an "effects" field """
            effects = [tag["name"] for tag in e["effects"]]

            if len(effects) > 0:
                returnValue = f"|{'|'.join(effects)}|"
        elif "resulttags" in e:
            """ This element is a Result element with a "resulttags" field """
            resulttags = [tag["name"] for tag in e["resulttags"]]

            if len(resulttags) > 0:
                returnValue = f"|{'|'.join(resulttags)}|"

        return returnValue

    def build_response(self):
        df = self.build_dataframe()
        if self.export_format == "tsv":
            return df.to_csv(sep="\t")
        elif self.export_format == "excel":
            return df.to_excel()
        else:
            raise ValueError(f"export_format not found: {self.export_format}")

    def build_dataframe(self) -> pd.DataFrame:
        raise NotImplementedError()
