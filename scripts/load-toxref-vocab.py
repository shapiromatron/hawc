import json
from pathlib import Path

import django
import pandas as pd
from django.conf import settings
from django.db import connection

from hawc.apps.vocab.constants import VocabularyNamespace, VocabularyTermType
from hawc.apps.vocab.models import Term

django.setup()

# ToxRef relevant columns
columns = [
    "endpoint_category",
    "endpoint_type",
    "endpoint_target",
    "effect_desc",
]

# Create new Term Objects - start fresh
Term.objects.all().delete()

df = pd.read_csv(Path(settings.PROJECT_PATH / "apps/vocab/fixtures/toxref.csv")).fillna("")[columns]
df.head()

# Clean up data
df["endpoint_category"] = df["endpoint_category"].str.strip()
df["endpoint_type"] = df["endpoint_type"].str.strip()
df["endpoint_target"] = df["endpoint_target"].str.strip()
df["effect_desc"] = df["effect_desc"].str.strip()

# build default lookup map
items = {key: {} for (key, value) in VocabularyTermType.choices}

# temp uid
i = 7000

# vocabulary import
for system in df["endpoint_category"].unique():
    s1 = df.query(f'`endpoint_category`=="{system}"')
    for effect in s1["endpoint_type"].unique():
        s2 = s1.query(f'`endpoint_type`=="{effect}"')
        for effect_subtype in s2["endpoint_target"].unique():
            s3 = s2.query(f'`endpoint_target`=="{effect_subtype}"')
            for name in s3["effect_desc"].unique():
                s4 = s3.query(f'`effect_desc`=="{name}"')

                # system
                system_key = system
                if system_key not in items[VocabularyTermType.system]:
                    obj = Term.objects.create(
                        namespace=VocabularyNamespace.ToxRef,
                        type=VocabularyTermType.system,
                        name=system,
                        uid=i,
                        parent_id=None,
                    )
                    i = i + 1
                    items[VocabularyTermType.system][system_key] = obj.id

                # effect
                effect_key = (system, effect)
                if effect_key not in items[VocabularyTermType.effect]:
                    obj = Term.objects.create(
                        namespace=VocabularyNamespace.ToxRef,
                        type=VocabularyTermType.effect,
                        name=effect,
                        uid=i,
                        parent_id=items[VocabularyTermType.system][system_key],
                    )
                    i = i + 1
                    items[VocabularyTermType.effect][effect_key] = obj.id
                # effect_subtype
                effect_subtype_key = (system, effect, effect_subtype)
                if effect_subtype_key not in items[VocabularyTermType.effect_subtype]:
                    obj = Term.objects.create(
                        namespace=VocabularyNamespace.ToxRef,
                        type=VocabularyTermType.effect_subtype,
                        name=effect_subtype,
                        uid=i,
                        parent_id=items[VocabularyTermType.effect][effect_key],
                    )
                    i = i + 1
                    items[VocabularyTermType.effect_subtype][effect_subtype_key] = obj.id
                # name
                name_key = (system, effect, effect_subtype, name)
                if name_key not in items[VocabularyTermType.endpoint_name]:
                    obj = Term.objects.create(
                        namespace=VocabularyNamespace.ToxRef,
                        type=VocabularyTermType.endpoint_name,
                        name=name,
                        uid=i,
                        parent_id=items[VocabularyTermType.effect_subtype][effect_subtype_key],
                    )
                    i = i + 1
                    items[VocabularyTermType.endpoint_name][name_key] = obj.id

Term.objects.count()

# change all uids to ids
for term in Term.objects.all():
    term.uid = term.id


def _get_headers(cursor) -> list[str]:
    cursor.execute("Select * FROM vocab_term LIMIT 0")
    return [desc[0] for desc in cursor.description]


# Generate the data fixture in JSONL instead of CSV
file = settings.PROJECT_PATH / "apps/vocab/fixtures/nested_toxref.jsonl"

with connection.client.connection.cursor() as cursor:
    headers = _get_headers(cursor)
    cursor.execute("SELECT * FROM vocab_term")
    data = cursor.fetchall()

    jsonl_data = []

    for row in data:
        row_dict = {header: row[i] for i, header in enumerate(headers)}
        print(row_dict)
        pk = row_dict["id"]

        fields = {}
        for i, header in enumerate(headers):
            # id should not be in fields
            if header != "id":
                fields[header] = row[i]

            # format dates - dateobj was throwing error
            if header == "created_on" or header == "last_updated":
                fields[header] = row[i].isoformat()

        # JSONL
        json_obj = {"model": "vocab.term", "pk": pk, "fields": fields}
        jsonl_data.append(json_obj)


with open(file, "w") as jsonl_file:
    for json_obj in jsonl_data:
        jsonl_file.write(json.dumps(json_obj) + "\n")
