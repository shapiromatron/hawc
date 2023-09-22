import pandas as pd


class Module:
    def __init__(
        self,
        key_prefix: str = "",
        query_prefix: str = "",
        include: tuple | None = None,
        exclude: tuple | None = None,
    ):
        # handle include, exclude, prefix?
        self.key_prefix = key_prefix + "-" if key_prefix else key_prefix
        self.query_prefix = query_prefix + "__" if query_prefix else query_prefix
        self.include = (key_prefix + field for field in include) if include else tuple()
        self.exclude = (key_prefix + field for field in exclude) if exclude else tuple()

    @property
    def value_map(self):
        if hasattr(self, "_value_map"):
            return self._value_map

        value_map = self._get_value_map()
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
    def annotation_map(self):
        if hasattr(self, "_annotation_map"):
            return self._annotation_map

        annotation_map = self._get_annotation_map(self.query_prefix)
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

    def _get_value_map(self):
        return {}

    def _get_annotation_map(self, query_prefix):
        return {}

    def _annotate(self, qs):
        if self.annotation_map:
            return qs.annotate(**self.annotation_map)
        return qs

    def _select_related(self, qs):
        # TODO: regex all keys in value_map, checking for greedy ending in __
        # then use that group as our select_related field ? how to handle prefetch_related ?
        # maybe remove this and just do it outside of module (ie in exporter)
        # if self.query_prefix:
        #    return qs.select_related(self.query_prefix)
        return qs

    def prepare_queryset(self, qs):
        qs = self._select_related(qs)
        qs = self._annotate(qs)
        return qs

    def prepare_df(self, df):
        # any manipulation that couldn't be handled by the ORM
        # if field missing, assume it was excluded
        # use map? something like set of fields to function?
        return df

    def get_df(self, qs):
        qs = self.prepare_queryset(qs)
        df = pd.DataFrame(
            data=qs.values_list(*self.value_map.values()), columns=list(self.value_map.keys())
        )
        return self.prepare_df(df)


class Exporter:
    def __init__(self):
        self._modules = [module[0](module[1], module[2]) for module in self.modules]

    def get_df(self, qs):
        for module in self._modules:
            qs = module.prepare_queryset(qs)
        values = [value for module in self._modules for value in module.value_map.values()]
        keys = [key for module in self._modules for key in module.value_map.keys()]
        df = pd.DataFrame(data=qs.values_list(*values), columns=keys)
        for module in self._modules:
            df = module.prepare_df(df)
        return df
