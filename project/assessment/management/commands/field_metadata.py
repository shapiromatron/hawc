from collections import defaultdict
from django.apps import apps
from django.core.management.base import BaseCommand
import os
import pandas as pd


HELP_TEXT = """Print HAWC field-level metadata"""


class Command(BaseCommand):
    help = HELP_TEXT

    def add_arguments(self, parser):
        parser.add_argument("excel_fn", type=str)

    def handle(self, excel_fn, **options):
        excel_fn = os.path.expanduser(excel_fn)
        dicts = defaultdict(list)
        for model in apps.get_models():
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            for fld in model._meta.fields:
                dicts["app_label"].append(app_label)
                dicts["model_name"].append(model_name)
                dicts["field_name"].append(fld.verbose_name or fld.name)
                dicts["field_type"].append(fld.__class__.__name__)
                dicts["field_help_text"].append(fld.help_text)
        df = pd.DataFrame(dicts)
        df = df[["app_label", "model_name", "field_name", "field_type", "field_help_text",]]
        df.to_excel(excel_fn, index=False)
