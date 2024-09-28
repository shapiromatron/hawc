import pandas as pd

from ..common.exports import Exporter, ModelExport


def expand_content(
    df: pd.DataFrame, content_column: str, prefix: str = "", flatten: bool = False
) -> pd.DataFrame:
    # expand JSON representation into individual columns
    df2 = df[content_column].dropna()
    df3 = pd.DataFrame(data=list(df2.values), index=df2.index).add_prefix(
        prefix if prefix else f"{content_column}-field-"
    )
    if flatten:
        lists = df3.columns[df3.iloc[0:10].map(lambda x: isinstance(x, list)).any()]
        df3[lists] = df3[lists].map(
            lambda el: "|".join(map(str, el)) if isinstance(el, list) else el
        )
    return df3


class ContentTypeExport(ModelExport):
    def get_value_map(self):
        return {
            "app": "app_label",
            "model": "model",
        }


class ModelUDFContentExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "object_id": "object_id",
            "content": "content",
            "created": "created",
            "last_updated": "last_updated",
        }

    def prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        if not df.empty:
            df2 = expand_content(df, content_column=self.get_column_name("content"))
            df = pd.merge(df, df2, how="left", left_index=True, right_index=True)
        return df


class ModelUDFContentExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            ContentTypeExport("content_type", "content_type"),
            ModelUDFContentExport(),
        ]


class TagUDFContentExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "reference": "reference",
            "tag": "tag_binding__tag",
            "content": "content",
            "created": "created",
            "last_updated": "last_updated",
        }

    def prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        if not df.empty:
            df2 = expand_content(df, content_column=self.get_column_name("content"))
            df = df.merge(df2, left_index=True, right_index=True)
        return df


class TagUDFContentExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            TagUDFContentExport(),
        ]


class ModelBindingExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "assessment": "assessment",
            "form_id": "form",
            "form_schema": "form__schema",
            "creator": "creator",
            "created": "created",
            "last_updated": "last_updated",
        }


class ModelBindingContentExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            ContentTypeExport("content_type", "content_type"),
            ModelBindingExport("model_binding", ""),
        ]


class TagBindingExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "assessment": "assessment",
            "tag": "tag",
            "form_id": "form",
            "form_schema": "form__schema",
            "creator": "creator",
            "created": "created",
            "last_updated": "last_updated",
        }


class TagBindingContentExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            TagBindingExport("tag_binding", ""),
        ]
