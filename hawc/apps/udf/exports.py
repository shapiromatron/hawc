import pandas as pd

from ..common.exports import Exporter, ModelExport


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
        # expand JSON representation into individual columns
        if df.shape[0] > 0 and "content-content" in df.columns:
            df2 = (
                pd.DataFrame(data=list(df["content-content"].values))
                .fillna("-")
                .add_prefix("content-field-")
            )
            df = df.merge(df2, left_index=True, right_index=True)
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
        # expand JSON representation into individual columns
        if df.shape[0] > 0 and "content-content" in df.columns:
            df2 = (
                pd.DataFrame(data=list(df["content-content"].values))
                .fillna("-")
                .add_prefix("content-field-")
            )
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
