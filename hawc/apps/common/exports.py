import pandas as pd
from django.conf import settings
from django.db.models import QuerySet

from .helper import FlatExport


class ModelExport:
    """Model level export module for use in Exporter class."""

    def __init__(
        self,
        key_prefix: str = "",
        query_prefix: str = "",
        include: tuple[str, ...] | None = None,
        exclude: tuple[str, ...] | None = None,
    ):
        self.key_prefix = key_prefix + "-" if key_prefix else key_prefix
        self.query_prefix = query_prefix + "__" if query_prefix else query_prefix
        self.include = tuple(self.key_prefix + field for field in include) if include else tuple()
        self.exclude = tuple(self.key_prefix + field for field in exclude) if exclude else tuple()

    @property
    def value_map(self) -> dict:
        """Value map of column names to ORM field names.

        This caches the result from get_value_map and applies any prefixes
        to the column names and ORM field names. It is also filtered down
        in compliance with any include/exclude parameters.

        Returns:
            dict: Value map
        """
        if hasattr(self, "_value_map"):
            return self._value_map

        value_map = self.get_value_map()
        # add key prefix
        if self.key_prefix:
            value_map = {self.key_prefix + k: v for k, v in value_map.items()}
        # add query prefix
        if self.query_prefix:
            value_map = {k: self.query_prefix + v for k, v in value_map.items()}
        # handle any includes
        if self.include:
            value_map = {k: v for k, v in value_map.items() if k in self.include}
        # handle any excludes
        if self.exclude:
            value_map = {k: v for k, v in value_map.items() if k not in self.exclude}

        self._value_map = value_map
        return self._value_map

    @property
    def annotation_map(self) -> dict:
        """Annotation map of annotated names to ORM expressions.

        This caches the result from get_annotation_map and applies any
        query_prefix to the annotated names. It is also filtered down
        in compliance with any include/exclude parameters.

        Returns:
            dict: Annotation map
        """
        if hasattr(self, "_annotation_map"):
            return self._annotation_map

        annotation_map = self.get_annotation_map(self.query_prefix)
        # add query prefix
        if self.query_prefix:
            annotation_map = {self.query_prefix + k: v for k, v in annotation_map.items()}
        # handle any includes/excludes
        if self.include or self.exclude:
            annotation_map = {
                k: v for k, v in annotation_map.items() if k in self.value_map.values()
            }

        self._annotation_map = annotation_map
        return self._annotation_map

    def get_value_map(self) -> dict:
        """Value map of column names to ORM field names.

        This should be overridden by any subclass where applicable.
        Prefixes and include/exclude should not be handled in this method;
        they are handled by the value_map property.

        Returns:
            dict: Value map
        """
        return {}

    def get_annotation_map(self, query_prefix: str) -> dict:
        """Annotation map of annotated names to ORM expressions.

        This should be overridden by any subclass where applicable.
        query_prefix for the annotated names and any include/exclude parameters
        are handled by the annotation_map property.
        query_prefix should still be used in the custom ORM expression
        values though, since there is no way to apply that through the
        annotation_map property.

        Returns:
            dict: Annotation map
        """
        return {}

    def get_column_name(self, name: str) -> str:
        """Get column name with key_prefix applied.

        Args:
            name (str): Column name

        Returns:
            str: Column name with prefix
        """
        return f"{self.key_prefix}{name}"

    def prepare_qs(self, qs: QuerySet) -> QuerySet:
        """Prepare the queryset for export.

        This includes applying any annotations if they exist.

        Args:
            qs (QuerySet): Queryset to prepare

        Returns:
            QuerySet: Prepared queryset
        """
        if self.annotation_map:
            return qs.annotate(**self.annotation_map)
        return qs

    def prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare the dataframe for export.

        This should be overridden by any subclass where applicable.
        Any data manipulations that couldn't be done by the ORM
        should be done in this method.

        Args:
            df (pd.DataFrame): Dataframe to manipulate

        Returns:
            pd.DataFrame: Manipulated dataframe
        """
        return df

    def format_time(self, df: pd.DataFrame) -> pd.DataFrame:
        for key in [self.get_column_name("created"), self.get_column_name("last_updated")]:
            if key in df.columns:
                df.loc[:, key] = df[key].apply(
                    lambda x: x.tz_convert(settings.TIME_ZONE).isoformat()
                )
        return df

    def get_df(self, qs: QuerySet) -> pd.DataFrame:
        """Get dataframe export from queryset.

        Args:
            qs (QuerySet): Queryset

        Returns:
            pd.DataFrame: Dataframe
        """
        qs = self.prepare_qs(qs)
        df = pd.DataFrame(
            data=qs.values_list(*self.value_map.values()), columns=list(self.value_map.keys())
        )
        return self.prepare_df(df)


class Exporter:
    """Data export for querysets.

    This class runs multiple ModelExports on a queryset
    and outputs a dataframe through the get_df method.
    """

    def build_modules(self) -> list[ModelExport]:
        """ModelExport instances to use for exporter.

        This should be overridden by any subclass.
        A key_prefix and query_prefix should be given to
        each ModelExport so that the column names don't clash
        and the ORM correctly navigates relationships.

        Returns:
            list[ModelExport]: List of ModelExports to build export with
        """
        raise NotImplementedError()

    def get_df(self, qs: QuerySet) -> pd.DataFrame:
        """Get dataframe export from queryset.

        Args:
            qs (QuerySet): Queryset

        Returns:
            pd.DataFrame: Dataframe
        """
        self._modules = self.build_modules()
        for module in self._modules:
            qs = module.prepare_qs(qs)
        values = [value for module in self._modules for value in module.value_map.values()]
        keys = [key for module in self._modules for key in module.value_map.keys()]
        df = pd.DataFrame(data=qs.values_list(*values), columns=keys)
        for module in self._modules:
            df = module.prepare_df(df)
        return df

    @classmethod
    def build_metadata(cls, df: pd.DataFrame) -> pd.DataFrame | None:
        return None

    @classmethod
    def flat_export(cls, qs: QuerySet, filename: str) -> FlatExport:
        """Return an instance of a FlatExport.
        Args:
            qs (QuerySet): the initial QuerySet
            filename (str): the filename for the export
        """
        df = cls().get_df(qs)
        return FlatExport(df=df, filename=filename, metadata=cls.build_metadata(df))
