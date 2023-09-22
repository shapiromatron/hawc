import json
import logging
import os
from operator import methodcaller

import pandas as pd
from django.apps import apps
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from docx import Document as create_document
from plotly.graph_objs._figure import Figure
from plotly.io import from_json
from pydantic import BaseModel as PydanticModel
from reversion import revisions as reversion
from treebeard.mp_tree import MP_Node

from hawc.tools.tables.ept import EvidenceProfileTable
from hawc.tools.tables.generic import BaseTable, GenericTable
from hawc.tools.tables.parser import QuillParser
from hawc.tools.tables.set import StudyEvaluationTable

from ..animal.exports import EndpointFlatDataPivot, EndpointGroupFlatDataPivot
from ..animal.models import Endpoint
from ..assessment.constants import EpiVersion
from ..assessment.models import Assessment, BaseEndpoint, DoseUnits
from ..common.helper import (
    FlatExport,
    HAWCDjangoJSONEncoder,
    PydanticToDjangoError,
    ReportExport,
    SerializerHelper,
    tryParseInt,
)
from ..common.models import get_model_copy_name
from ..common.validators import validate_html_tags, validate_hyperlinks
from ..eco.exports import EcoFlatComplete
from ..epi.exports import OutcomeDataPivot
from ..epimeta.exports import MetaResultFlatDataPivot
from ..epiv2.exports import EpiFlatComplete
from ..invitro import exports as ivexports
from ..riskofbias.models import RiskOfBiasScore
from ..riskofbias.serializers import AssessmentRiskOfBiasSerializer
from ..study.models import Study
from . import constants, managers, prefilters

logger = logging.getLogger(__name__)


class SummaryText(MP_Node):
    objects = managers.SummaryTextManager()

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used on the website to describe this object (no spaces or special-characters).",
        unique=True,
    )
    text = models.TextField(default="")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        verbose_name_plural = "Summary Text Descriptions"
        unique_together = (
            ("assessment", "title"),
            ("assessment", "slug"),
        )

    def __str__(self):
        return self.title

    @classmethod
    def assessment_qs(cls, assessment_id):
        return cls.objects.filter(assessment=assessment_id)

    @classmethod
    def get_assessment_root_node(cls, assessment_id):
        return SummaryText.objects.get(title=f"assessment-{assessment_id}")

    @classmethod
    def get_assessment_queryset(cls, assessment_id):
        return cls.get_assessment_root_node(assessment_id).get_descendants()

    @classmethod
    def build_default(cls, assessment):
        assessment = SummaryText.add_root(
            assessment=assessment,
            title=f"assessment-{assessment.pk}",
            slug=f"assessment-{assessment.pk}-slug",
            text="Root-level text",
        )

    @classmethod
    def get_assessment_descendants(cls, assessment_id, json_encode=True):
        """
        Return all, excluding root
        """
        root = cls.get_assessment_root_node(assessment_id)
        tags = SummaryText.dump_bulk(root)

        if json_encode:
            return json.dumps(tags, cls=HAWCDjangoJSONEncoder)
        else:
            return tags

    @classmethod
    def get_assessment_qs(cls, assessment_id):
        """
        Return queryset, including root.
        """
        root = cls.get_assessment_root_node(assessment_id)
        return cls.get_tree(parent=root)

    def get_absolute_url(self):
        return f"{reverse('summary:list', args=(self.assessment_id,))}#{self.slug}"

    def get_assessment(self):
        return self.assessment


class SummaryTable(models.Model):
    objects = managers.SummaryTableManager()

    TABLE_SCHEMA_MAP = {
        constants.TableType.GENERIC: GenericTable,
        constants.TableType.EVIDENCE_PROFILE: EvidenceProfileTable,
        constants.TableType.STUDY_EVALUATION: StudyEvaluationTable,
    }

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used to describe this object "
        "(no spaces or special-characters).",
    )
    content = models.JSONField(default=dict)
    table_type = models.PositiveSmallIntegerField(
        choices=constants.TableType.choices, default=constants.TableType.GENERIC
    )
    published = models.BooleanField(
        default=False,
        verbose_name="Publish table for public viewing",
        help_text="For assessments marked for public viewing, mark table to be viewable by public",
    )
    caption = models.TextField(blank=True, validators=[validate_html_tags, validate_hyperlinks])
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        unique_together = (
            ("assessment", "title"),
            ("assessment", "slug"),
        )

    def __str__(self):
        return self.title

    def get_assessment(self):
        return self.assessment

    @classmethod
    def get_list_url(cls, assessment_id: int):
        return reverse("summary:tables_list", args=(assessment_id,))

    @classmethod
    def get_api_list_url(cls, assessment_id: int):
        return reverse("summary:api:summary-table-list") + f"?assessment_id={assessment_id}"

    def get_absolute_url(self):
        return reverse(
            "summary:tables_detail",
            args=(
                self.assessment_id,
                self.slug,
            ),
        )

    def get_update_url(self):
        return reverse(
            "summary:tables_update",
            args=(
                self.assessment_id,
                self.slug,
            ),
        )

    def get_delete_url(self):
        return reverse(
            "summary:tables_delete",
            args=(
                self.assessment_id,
                self.slug,
            ),
        )

    def get_api_url(self):
        return reverse("summary:api:summary-table-detail", args=(self.id,))

    def get_api_word_url(self):
        return reverse("summary:api:summary-table-docx", args=(self.id,))

    def get_content_schema_class(self):
        if self.table_type not in self.TABLE_SCHEMA_MAP:
            raise ValueError(f"Table type not found: {self.table_type}")
        return self.TABLE_SCHEMA_MAP[self.table_type]

    def get_table(self) -> BaseTable:
        schema_class = self.get_content_schema_class()
        # ensure the assessment id is from the object; not custom config
        kwargs = {}
        if "assessment_id" in schema_class.schema()["properties"]:
            kwargs["assessment_id"] = self.assessment_id
        return schema_class.parse_obj(dict(self.content, **kwargs))

    @classmethod
    def build_default(cls, assessment_id: int, table_type: int) -> "SummaryTable":
        """Build an incomplete, but default SummaryTable instance"""
        instance = cls(assessment_id=assessment_id, table_type=table_type)
        schema = instance.get_content_schema_class()
        instance.content = schema.get_default_props()
        return instance

    def to_docx(self, base_url: str = "", landscape: bool = True):
        docx = create_document()
        parser = QuillParser(base_url=base_url)
        docx.add_heading(self.title)
        url = self.get_absolute_url()
        parser.feed(f'<p><a href="{url}">View Online</a></p>', docx)
        table = self.get_table()
        table.to_docx(parser=parser, docx=docx, landscape=landscape)
        if self.caption:
            parser.feed(self.caption, docx)
        return ReportExport(docx=docx, filename=self.slug)

    @classmethod
    def get_data(cls, table_type: int, assessment_id: int, **kwargs):
        return cls.TABLE_SCHEMA_MAP[table_type].get_data(assessment_id=assessment_id, **kwargs)

    def clean(self):
        # make sure table can be built
        with PydanticToDjangoError(field="content"):
            try:
                self.get_table()
            except ValueError as e:
                raise ValidationError({"content": str(e)})

        # clean up control characters before string validation
        content_str = json.dumps(self.content).replace('\\"', '"')

        # validate tags used in text
        validate_html_tags(content_str, "content")
        validate_hyperlinks(content_str, "content")


class HeatmapDataset(PydanticModel):
    type: str
    name: str
    url: str


class HeatmapDatasets(PydanticModel):
    datasets: list[HeatmapDataset]


class Visual(models.Model):
    objects = managers.VisualManager()

    FAKE_INITIAL_ID = -1

    title = models.CharField(max_length=128)
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used to describe this object "
        "(no spaces or special-characters).",
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="visuals")
    visual_type = models.PositiveSmallIntegerField(choices=constants.VisualType.choices)
    dose_units = models.ForeignKey(DoseUnits, on_delete=models.SET_NULL, blank=True, null=True)
    endpoints = models.ManyToManyField(
        BaseEndpoint,
        related_name="visuals",
        help_text="Endpoints to be included in visualization",
        blank=True,
    )
    settings = models.JSONField(default=dict)
    caption = models.TextField(blank=True)
    published = models.BooleanField(
        default=False,
        verbose_name="Publish visual for public viewing",
        help_text="For assessments marked for public viewing, mark visual to be viewable by public",
    )
    sort_order = models.CharField(
        max_length=40,
        choices=constants.SortOrder.choices,
        default=constants.SortOrder.SC,
    )
    prefilters = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        unique_together = (("assessment", "slug"),)

    def __str__(self):
        return self.title

    @staticmethod
    def get_list_url(assessment_id):
        return reverse("summary:visualization_list", args=(assessment_id,))

    def get_absolute_url(self):
        return reverse("summary:visualization_detail", args=(self.assessment_id, self.slug))

    def get_update_url(self):
        return reverse("summary:visualization_update", args=(self.assessment_id, self.slug))

    def get_delete_url(self):
        return reverse("summary:visualization_delete", args=(self.assessment_id, self.slug))

    def get_assessment(self):
        return self.assessment

    def get_api_detail(self):
        return reverse("summary:api:visual-detail", args=(self.id,))

    def get_data_url(self):
        return reverse("summary:api:visual-data", args=(self.id,))

    def get_api_heatmap_datasets(self):
        return reverse("summary:api:assessment-heatmap-datasets", args=(self.assessment_id,))

    @classmethod
    def get_heatmap_datasets(cls, assessment: Assessment) -> HeatmapDatasets:
        datasets = [
            HeatmapDataset(
                type="Literature",
                name="Literature summary",
                url=reverse("lit:api:assessment-tag-heatmap", args=(assessment.id,)),
            )
        ]
        if assessment.has_animal_data:
            datasets.extend(
                [
                    HeatmapDataset(
                        type="Bioassay",
                        name="Bioassay study design",
                        url=reverse("animal:api:assessment-study-heatmap", args=(assessment.id,)),
                    ),
                    HeatmapDataset(
                        type="Bioassay",
                        name="Bioassay study design (including unpublished HAWC data)",
                        url=reverse("animal:api:assessment-study-heatmap", args=(assessment.id,))
                        + "?unpublished=true",
                    ),
                    HeatmapDataset(
                        type="Bioassay",
                        name="Bioassay endpoint summary",
                        url=reverse(
                            "animal:api:assessment-endpoint-heatmap", args=(assessment.id,)
                        ),
                    ),
                    HeatmapDataset(
                        type="Bioassay",
                        name="Bioassay endpoint summary (including unpublished HAWC data)",
                        url=reverse("animal:api:assessment-endpoint-heatmap", args=(assessment.id,))
                        + "?unpublished=true",
                    ),
                    HeatmapDataset(
                        type="Bioassay",
                        name="Bioassay endpoint with doses",
                        url=reverse(
                            "animal:api:assessment-endpoint-doses-heatmap", args=(assessment.id,)
                        ),
                    ),
                    HeatmapDataset(
                        type="Bioassay",
                        name="Bioassay endpoint with doses (including unpublished HAWC data)",
                        url=reverse(
                            "animal:api:assessment-endpoint-doses-heatmap", args=(assessment.id,)
                        )
                        + "?unpublished=true",
                    ),
                ]
            )
        if assessment.has_epi_data:
            if assessment.epi_version == EpiVersion.V1:
                datasets.extend(
                    [
                        HeatmapDataset(
                            type="Epi",
                            name="Epidemiology study design",
                            url=reverse("epi:api:assessment-study-heatmap", args=(assessment.id,)),
                        ),
                        HeatmapDataset(
                            type="Epi",
                            name="Epidemiology study design (including unpublished HAWC data)",
                            url=reverse("epi:api:assessment-study-heatmap", args=(assessment.id,))
                            + "?unpublished=true",
                        ),
                        HeatmapDataset(
                            type="Epi",
                            name="Epidemiology result summary",
                            url=reverse("epi:api:assessment-result-heatmap", args=(assessment.id,)),
                        ),
                        HeatmapDataset(
                            type="Epi",
                            name="Epidemiology result summary (including unpublished HAWC data)",
                            url=reverse("epi:api:assessment-result-heatmap", args=(assessment.id,))
                            + "?unpublished=true",
                        ),
                    ]
                )
            elif assessment.epi_version == EpiVersion.V2:
                datasets.extend(
                    [
                        HeatmapDataset(
                            type="Epi",
                            name="Epidemiology evidence map",
                            url=reverse("epiv2:api:assessment-study-export", args=(assessment.id,)),
                        ),
                        HeatmapDataset(
                            type="Epi",
                            name="Epidemiology data extractions",
                            url=reverse("epiv2:api:assessment-export", args=(assessment.id,)),
                        ),
                    ]
                )
            else:
                raise ValueError("Unknown epi data type")
        additional_datasets = [
            HeatmapDataset(type="Dataset", name=f"Dataset: {ds.name}", url=ds.get_api_data_url())
            for ds in assessment.datasets.all()
        ]
        datasets.extend(additional_datasets)
        return HeatmapDatasets(datasets=datasets)

    @staticmethod
    def get_dose_units():
        return DoseUnits.objects.json_all()

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def get_filterset_class(self):
        return prefilters.VisualTypePrefilter.from_visual_type(self.visual_type).value

    def get_filterset(self, data, assessment, **kwargs):
        return self.get_filterset_class()(data=data, assessment=assessment, **kwargs)

    def get_request_prefilters(self, request):
        # find all keys that start with "prefilters-" prefix
        prefix = "prefilters-"
        return {
            key[len(prefix) :]: value
            for key, value in request.POST.lists()
            if key.startswith(prefix)
        }

    def get_endpoints(self, request=None) -> models.QuerySet[Endpoint]:
        if self.visual_type == constants.VisualType.BIOASSAY_AGGREGATION:
            ids = (
                request.POST.getlist("endpoints")
                if request
                else self.endpoints.values_list("id", flat=True)
            )
            return Endpoint.objects.assessment_qs(self.assessment).filter(id__in=ids)

        elif self.visual_type == constants.VisualType.BIOASSAY_CROSSVIEW:
            dose_units_id = (
                tryParseInt(request.POST.get("dose_units"), -1) if request else self.dose_units_id
            )
            filters = {"animal_group__dosing_regime__doses__dose_units_id": dose_units_id}

            prefilters = self.get_request_prefilters(request) if request else self.prefilters
            fs = self.get_filterset(prefilters, self.assessment)
            form = fs.form
            fs.set_passthrough_options(form)
            fs.form.is_valid()
            return fs.qs.filter(**filters).distinct("id")

        return Endpoint.objects.none()

    def get_studies(self, request=None) -> models.QuerySet[Study] | list[Study]:
        """
        If there are endpoint-level prefilters, we get all studies which
        match this criteria. Otherwise, we use the M2M list of studies attached
        to the model.
        """
        qs = Study.objects.none()
        filters = {}

        if self.visual_type in [
            constants.VisualType.ROB_HEATMAP,
            constants.VisualType.ROB_BARCHART,
        ]:
            prefilters = self.get_request_prefilters(request) if request else self.prefilters
            fs = self.get_filterset(prefilters, self.assessment)
            form = fs.form
            fs.set_passthrough_options(form)
            fs.form.is_valid()
            cleaned_prefilters = fs.form.cleaned_data

            # TODO - fix - we should use a different set of prefilters for studies
            study_fields = ["published_only", "studies"]
            endpoint_prefilters = {
                k: v for k, v in cleaned_prefilters.items() if k not in study_fields
            }
            if any(value for value in endpoint_prefilters.values()):
                endpoint_qs = fs.qs
                filters["id__in"] = set(
                    endpoint_qs.values_list("animal_group__experiment__study_id", flat=True)
                )
            else:
                if f := cleaned_prefilters.pop(study_fields[0], False):
                    filters["published"] = f
                if f := cleaned_prefilters.get(study_fields[1], []):
                    filters["id__in"] = f

            qs = Study.objects.assessment_qs(self.assessment).filter(**filters)

        # TODO - remove? handle sort order in visualization?
        if self.sort_order:
            if self.sort_order == constants.SortOrder.OC.value:
                qs = sorted(qs, key=methodcaller("get_overall_confidence"), reverse=True)
            else:
                qs = qs.order_by(self.sort_order)

        return qs

    def get_editing_dataset(self, request):
        # Generate a pseudo-return when editing or creating a dataset.
        # Do not include the settings field; this will be set from the
        # input-form. Should approximately mirror the Visual API from rest-framework.

        dose_units = None
        try:
            dose_units = int(request.POST.get("dose_units"))
        except (TypeError, ValueError):
            # TypeError if dose_units is None; ValueError if dose_units is ""
            pass

        return {
            "assessment": self.assessment_id,
            "assessment_rob_name": self.assessment.get_rob_name_display(),
            "title": request.POST.get("title"),
            "slug": request.POST.get("slug"),
            "caption": request.POST.get("caption"),
            "dose_units": dose_units,
            "created": timezone.now().isoformat(),
            "last_updated": timezone.now().isoformat(),
            "rob_settings": AssessmentRiskOfBiasSerializer(self.assessment).data,
            "endpoints": [
                SerializerHelper.get_serialized(e, json=False) for e in self.get_endpoints(request)
            ],
            "studies": [
                SerializerHelper.get_serialized(s, json=False) for s in self.get_studies(request)
            ],
        }

    def _update_settings_across_assessments(self, cw: dict) -> str:
        settings = json.loads(self.settings)

        if (
            self.visual_type == constants.VisualType.BIOASSAY_CROSSVIEW
        ) and "included_metrics" in settings:
            pass

        if (
            self.visual_type
            in [constants.VisualType.ROB_BARCHART, constants.VisualType.ROB_HEATMAP]
        ) and "included_metrics" in settings:
            ids = []
            model_cw = cw[get_model_copy_name(apps.get_model("riskofbias", "RiskOfBiasMetric"))]
            for id_ in settings["included_metrics"]:
                if id_ in model_cw:
                    ids.append(model_cw[id_])
            settings["included_metrics"] = ids

        return json.dumps(settings)

    def get_rob_visual_type_display(self, value):
        rob_name = self.assessment.get_rob_name_display().lower()
        return value.replace("risk of bias", rob_name)

    def get_plotly_from_json(self) -> Figure:
        if self.visual_type != constants.VisualType.PLOTLY:
            raise ValueError("Incorrect visual type")
        try:
            return from_json(json.dumps(self.settings))
        except ValueError as err:
            raise ValueError(err)

    def _rob_data_qs(self, use_settings: bool = True) -> models.QuerySet:
        study_ids = list(self.get_studies().values_list("id", flat=True))
        settings = self.settings

        qs = RiskOfBiasScore.objects.filter(
            riskofbias__active=True,
            riskofbias__final=True,
            riskofbias__study__in=study_ids,
        )

        # use settings in read-only view; dont use when configuring plot
        if use_settings:
            qs = qs.filter(metric__in=settings["included_metrics"]).exclude(
                id__in=settings.get("excluded_score_ids", [])
            )
        return qs

    def data_df(self, use_settings: bool = True) -> pd.DataFrame:
        if self.visual_type not in [
            constants.VisualType.ROB_BARCHART,
            constants.VisualType.ROB_HEATMAP,
        ]:
            raise ValueError("Not supported for this visual type")
        return self._rob_data_qs(use_settings=use_settings).df()


class DataPivot(models.Model):
    objects = managers.DataPivotManager()

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=128,
        help_text="Enter the title of the visualization (spaces and special-characters allowed).",
    )
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used to describe this object "
        "(no spaces or special-characters).",
    )
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="To clone settings from an existing data-pivot, copy them into this field, "
        "otherwise leave blank.",
    )
    caption = models.TextField(blank=True, default="")
    published = models.BooleanField(
        default=False,
        verbose_name="Publish visual for public viewing",
        help_text="For assessments marked for public viewing, mark visual to be viewable by public",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        unique_together = (("assessment", "slug"),)
        ordering = ("title",)

    def __str__(self):
        return self.title

    def save(self, **kw):
        if self.settings is None:
            self.settings = {}
        return super().save(**kw)

    @staticmethod
    def get_list_url(assessment_id):
        return reverse("summary:visualization_list", args=[str(assessment_id)])

    def get_absolute_url(self):
        return reverse("summary:dp_detail", args=(self.assessment_id, self.slug))

    def get_visualization_update_url(self):
        return reverse("summary:dp_update", args=(self.assessment_id, self.slug))

    def get_assessment(self):
        return self.assessment

    def get_api_detail(self):
        return reverse("summary:api:data_pivot-detail", args=(self.id,))

    def get_download_url(self):
        return reverse("summary:api:data_pivot-data", args=(self.id,))

    def get_data_url(self):
        return self.get_download_url() + "?format=tsv"

    def get_dataset(self) -> FlatExport:
        if hasattr(self, "datapivotupload"):
            return self.datapivotupload.get_dataset()
        else:
            return self.datapivotquery.get_dataset()

    @property
    def visual_type(self):
        if hasattr(self, "datapivotupload"):
            return self.datapivotupload.visual_type
        else:
            return self.datapivotquery.visual_type

    def get_visual_type_display(self):
        return self.visual_type

    @staticmethod
    def reset_row_overrides(settings: dict):
        settings["row_overrides"] = []


class DataPivotUpload(DataPivot):
    objects = managers.DataPivotUploadManager()

    excel_file = models.FileField(
        verbose_name="Excel file",
        upload_to="data_pivot_excel",
        max_length=250,
        help_text="Upload an Excel file in XLSX format.",
    )
    worksheet_name = models.CharField(
        help_text="Worksheet name to use in Excel file. If blank, the first worksheet is used.",
        max_length=64,
        blank=True,
    )

    @property
    def visual_type(self):
        return "Data pivot (file upload)"

    def _update_settings_across_assessments(self, cw: dict) -> str:
        # no changes required
        return self.settings

    def get_dataset(self) -> FlatExport:
        worksheet_name = self.worksheet_name if len(self.worksheet_name) > 0 else 0
        df = pd.read_excel(self.excel_file.file, sheet_name=worksheet_name)
        filename = os.path.splitext(os.path.basename(self.excel_file.file.name))[0]
        return FlatExport(df=df, filename=filename)


class DataPivotQuery(DataPivot):
    objects = managers.DataPivotQueryManager()

    MAXIMUM_QUERYSET_COUNT = 1000

    evidence_type = models.PositiveSmallIntegerField(
        choices=constants.StudyType.choices, default=constants.StudyType.BIOASSAY
    )
    export_style = models.PositiveSmallIntegerField(
        choices=constants.ExportStyle.choices,
        default=constants.ExportStyle.EXPORT_GROUP,
        help_text="The export style changes the level at which the "
        "data are aggregated, and therefore which columns and types "
        "of data are presented in the export, for use in the visual.",
    )
    # Implementation-note: use ArrayField to save DoseUnits ManyToMany because
    # order is important and it would be a much larger implementation to allow
    # copying and saving dose-units- dose-units are rarely deleted and this
    # implementation shouldn't cause issues with deletions because should be
    # used primarily with id__in style queries.
    preferred_units = ArrayField(
        models.PositiveIntegerField(),
        default=list,
        help_text="List of preferred dose-values, in order of preference. "
        "If empty, dose-units will be random for each endpoint "
        "presented. This setting may used for comparing "
        "percent-response, where dose-units are not needed, or for "
        "creating one plot similar, but not identical, dose-units.",
    )
    prefilters = models.JSONField(default=dict)

    def clean(self):
        count = self.get_queryset().count()

        if count == 0:
            err = """
                Current settings returned 0 results. Please update your settings to make
                data filters less restrictive.
            """
            raise ValidationError(err)

        if count > self.MAXIMUM_QUERYSET_COUNT:
            err = f"""
                Current settings returned too many results ({count} returned; a maximum of
                {self.MAXIMUM_QUERYSET_COUNT} are allowed). Please update your settings to make
                data filters more restrictive.
            """
            raise ValidationError(err)

    def _get_dataset_exporter(self, qs):
        if self.evidence_type == constants.StudyType.BIOASSAY:
            # select export class
            if self.export_style == constants.ExportStyle.EXPORT_GROUP:
                ExportClass = EndpointGroupFlatDataPivot
            elif self.export_style == constants.ExportStyle.EXPORT_ENDPOINT:
                ExportClass = EndpointFlatDataPivot

            exporter = ExportClass(
                qs,
                assessment=self.assessment,
                filename=f"{self.assessment}-animal-bioassay",
                preferred_units=self.preferred_units,
            )

        elif self.evidence_type == constants.StudyType.EPI:
            if self.assessment.epi_version == EpiVersion.V1:
                exporter = OutcomeDataPivot(
                    qs,
                    assessment=self.assessment,
                    filename=f"{self.assessment}-epi",
                )
            else:
                exporter = EpiFlatComplete(
                    qs,
                    assessment=self.assessment,
                    filename=f"{self.assessment}-epi",
                )

        elif self.evidence_type == constants.StudyType.EPI_META:
            exporter = MetaResultFlatDataPivot(
                qs,
                assessment=self.assessment,
                filename=f"{self.assessment}-epi",
            )

        elif self.evidence_type == constants.StudyType.IN_VITRO:
            # select export class
            if self.export_style == constants.ExportStyle.EXPORT_GROUP:
                Exporter = ivexports.DataPivotEndpointGroup
            elif self.export_style == constants.ExportStyle.EXPORT_ENDPOINT:
                Exporter = ivexports.DataPivotEndpoint

            # generate export
            exporter = Exporter(
                qs,
                assessment=self.assessment,
                filename=f"{self.assessment}-invitro",
            )

        elif self.evidence_type == constants.StudyType.ECO:
            exporter = EcoFlatComplete(
                qs,
                assessment=self.assessment,
                filename=f"{self.assessment}-eco",
            )

        return exporter

    def get_filterset_class(self):
        return prefilters.StudyTypePrefilter.from_study_type(
            self.evidence_type, self.assessment
        ).value

    def get_filterset(self, data, assessment, **kwargs):
        return self.get_filterset_class()(data=data, assessment=assessment, **kwargs)

    def get_queryset(self):
        fs = self.get_filterset(self.prefilters, self.assessment)
        form = fs.form
        fs.set_passthrough_options(form)
        qs = fs.qs
        if self.evidence_type == constants.StudyType.BIOASSAY and self.preferred_units:
            qs = qs.filter(animal_group__dosing_regime__doses__dose_units__in=self.preferred_units)
        return qs.order_by("id")

    def get_dataset(self) -> FlatExport:
        qs = self.get_queryset()
        exporter = self._get_dataset_exporter(qs)
        return exporter.build_export()

    @property
    def visual_type(self):
        if self.evidence_type == constants.StudyType.BIOASSAY:
            return "Data pivot (animal bioassay)"
        elif self.evidence_type == constants.StudyType.EPI:
            return "Data pivot (epidemiology)"
        elif self.evidence_type == constants.StudyType.EPI_META:
            return "Data pivot (epidemiology meta-analysis/pooled-analysis)"
        elif self.evidence_type == constants.StudyType.IN_VITRO:
            return "Data pivot (in vitro)"
        elif self.evidence_type == constants.StudyType.ECO:
            return "Data pivot (ecology)"
        else:
            raise ValueError("Unknown type")

    def _update_settings_across_assessments(self, cw: dict) -> str:
        try:
            settings = json.loads(self.settings)
        except json.JSONDecodeError:
            return self.settings

        if len(settings["row_overrides"]) > 0:
            if (
                self.evidence_type == constants.StudyType.BIOASSAY
                and self.export_style == constants.ExportStyle.EXPORT_GROUP
            ):
                Model = apps.get_model("animal", "EndpointGroup")
            elif (
                self.evidence_type == constants.StudyType.BIOASSAY
                and self.export_style == constants.ExportStyle.EXPORT_ENDPOINT
            ):
                Model = apps.get_model("animal", "Endpoint")
            elif (
                self.evidence_type == constants.StudyType.EPI
                and self.export_style == constants.ExportStyle.EXPORT_GROUP
            ):
                Model = apps.get_model("epi", "ResultGroup")
            elif (
                self.evidence_type == constants.StudyType.EPI
                and self.export_style == constants.ExportStyle.EXPORT_ENDPOINT
            ):
                Model = apps.get_model("epi", "Outcome")
            else:
                raise NotImplementedError()

            model_cw = cw[get_model_copy_name(Model)]
            for override in settings["row_overrides"]:
                override.update(pk=model_cw[override["pk"]])

        return json.dumps(settings)


reversion.register(SummaryText)
reversion.register(SummaryTable)
reversion.register(DataPivot)
reversion.register(DataPivotUpload)
reversion.register(DataPivotQuery)
reversion.register(Visual)
