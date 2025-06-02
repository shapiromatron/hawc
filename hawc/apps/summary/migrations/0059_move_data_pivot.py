from io import BytesIO
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import migrations

from hawc.apps.summary.constants import StudyType, VisualType


def create_dataset(
    apps,
    assessment_id: int,
    name: str,
    description: str,
    data: BytesIO,
    df: pd.DataFrame,
    data_name: str,
    published: bool = True,
    excel_worksheet_name: str = "",
    notes: str = "",
):
    Dataset = apps.get_model("assessment", "Dataset")
    DatasetRevision = apps.get_model("assessment", "DatasetRevision")
    dataset = Dataset.objects.create(
        assessment_id=assessment_id,
        name=name,
        description=description,
        published=published,
    )
    DatasetRevision.objects.create(
        dataset=dataset,
        version=1,
        data=ContentFile(data.getvalue(), name=data_name),
        excel_worksheet_name=excel_worksheet_name,
        metadata=dict(
            filename=data_name,
            extension=".xlsx",
            num_rows=df.shape[0],
            num_columns=df.shape[1],
            column_names=df.columns.tolist(),
        ),
        notes=notes,
    )
    return dataset


def forward(apps, schema_editor):
    Dataset = apps.get_model("assessment", "Dataset")
    LabeledItem = apps.get_model("assessment", "LabeledItem")
    Visual = apps.get_model("summary", "Visual")
    DataPivotQuery = apps.get_model("summary", "DataPivotQuery")
    DataPivotUpload = apps.get_model("summary", "DataPivotUpload")
    viz_ct = ContentType.objects.get_for_model(Visual).id
    dpq_ct = ContentType.objects.get_for_model(DataPivotQuery).id
    dpu_ct = ContentType.objects.get_for_model(DataPivotUpload).id

    mapping = []
    dps = []

    for dp in DataPivotQuery.objects.all():
        new_dp_id = (
            f"{dp.slug}-dp"
            if Visual.objects.filter(assessment_id=dp.assessment_id, slug=dp.slug).exists()
            else dp.slug
        )

        visualization = Visual(
            title=dp.title,
            slug=new_dp_id,
            assessment=dp.assessment,
            evidence_type=dp.evidence_type,
            visual_type=VisualType.DATA_PIVOT_QUERY,
            settings=dp.settings,
            caption=dp.caption,
            published=dp.published,
            prefilters={
                "export_style": dp.export_style,
                "preferred_units": dp.preferred_units,
                "prefilters": dp.prefilters,
            },
            dp_id=dp.id,
            dp_slug=dp.slug,
            created=dp.created,
            last_updated=dp.last_updated,
        )
        visualization.save()

        mapping.append(("dpq", dp.id, visualization.id))

        visualization.created = dp.created
        visualization.last_updated = dp.last_updated
        dps.append(visualization)

        for label in LabeledItem.objects.filter(object_id=dp.id, content_type_id=dpq_ct):
            label.content_type_id = viz_ct
            label.object_id = visualization.id
            label.save()

    for dp in DataPivotUpload.objects.all():
        new_dp_id = (
            f"{dp.slug}-dp"
            if Visual.objects.filter(assessment_id=dp.assessment_id, slug=dp.slug).exists()
            else dp.slug
        )
        new_ds_name = (
            f"{dp.title} dp"
            if Dataset.objects.filter(assessment_id=dp.assessment_id, name=dp.title).exists()
            else dp.title
        )

        if settings.DEBUG:
            df = pd.DataFrame(data=[[1, 2], [3, 4]], columns=("a", "b"))
            data = BytesIO(b"debugging")
        else:
            worksheet_name = dp.worksheet_name or 0
            df = pd.read_excel(dp.excel_file.file, sheet_name=worksheet_name)
            data = BytesIO(dp.excel_file.file.read())

        dataset = create_dataset(
            apps,
            assessment_id=dp.assessment_id,
            name=new_ds_name,
            description=dp.caption,
            data=data,
            df=df,
            data_name=Path(dp.excel_file.name).name,
            published=True,
            excel_worksheet_name=dp.worksheet_name,
            notes="",
        )
        visualization = Visual(
            title=dp.title,
            slug=new_dp_id,
            assessment=dp.assessment,
            visual_type=VisualType.DATA_PIVOT_FILE,
            evidence_type=StudyType.OTHER,
            settings=dp.settings,
            caption=dp.caption,
            published=dp.published,
            dataset=dataset,
            prefilters={},
            dp_id=dp.id,
            dp_slug=dp.slug,
            created=dp.created,
            last_updated=dp.last_updated,
        )
        visualization.save()

        mapping.append(("dpu", dp.id, visualization.id))

        visualization.created = dp.created
        visualization.last_updated = dp.last_updated
        dps.append(visualization)

        for label in LabeledItem.objects.filter(object_id=dp.id, content_type_id=dpu_ct):
            label.content_type_id = viz_ct
            label.object_id = visualization.id
            label.save()

    Visual.objects.bulk_update(dps, fields=("created", "last_updated"))

    pd.DataFrame(data=mapping, columns="model|old_id|new_id".split("|")).to_csv(
        "summary-migration-0059.csv", index=False
    )


def backward(apps, schema_editor):
    Dataset = apps.get_model("summary", "Visual")
    Visual = apps.get_model("summary", "Visual")
    Dataset.objects.filter(
        id__in=Visual.objects.filter(visual_type=VisualType.DATA_PIVOT_FILE).values_list(
            "dataset_id", flat=True
        )
    ).delete()
    Visual.objects.filter(
        visual_type__in=[VisualType.DATA_PIVOT_QUERY, VisualType.DATA_PIVOT_FILE]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("summary", "0058_migrate_data_pivot")]
    operations = [migrations.RunPython(forward, reverse_code=backward)]
