import json
import logging
import os
from operator import methodcaller
from typing import Dict, List

from django.apps import apps
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from pydantic import BaseModel as PydanticModel
from reversion import revisions as reversion
from treebeard.mp_tree import MP_Node

from ..animal.exports import EndpointFlatDataPivot, EndpointGroupFlatDataPivot
from ..animal.models import Endpoint
from ..assessment.models import Assessment, BaseEndpoint, DoseUnits
from ..common.helper import (
    FlatExport,
    HAWCDjangoJSONEncoder,
    HAWCtoDateString,
    SerializerHelper,
    read_excel,
    tryParseInt,
)
from ..common.models import get_model_copy_name
from ..epi.exports import OutcomeDataPivot
from ..epi.models import Outcome
from ..epimeta.exports import MetaResultFlatDataPivot
from ..epimeta.models import MetaResult
from ..invitro import exports as ivexports
from ..invitro.models import IVEndpoint
from ..study.models import Study
from . import managers

logger = logging.getLogger(__name__)

BIOASSAY = 0
EPI = 1
EPI_META = 4
IN_VITRO = 2
OTHER = 3

STUDY_TYPE_CHOICES = (
    (BIOASSAY, "Animal Bioassay"),
    (EPI, "Epidemiology"),
    (EPI_META, "Epidemiology meta-analysis/pooled analysis"),
    (IN_VITRO, "In vitro"),
    (OTHER, "Other"),
)


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
        return f"{reverse('summary:list', kwargs={'assessment': self.assessment.pk})}#{self.slug}"

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_report(cls, report, assessment):
        title = "Summary Text: " + HAWCtoDateString(timezone.now())
        report.doc.add_heading(title, level=1)

        preface = "Preliminary summary-text export in Word (work in progress)"
        p = report.doc.add_paragraph(preface)
        p.italic = True

        def print_node(node, depth):
            report.doc.add_heading(node["data"]["title"], level=depth)
            report.doc.add_paragraph(strip_tags(node["data"]["text"]))
            if node.get("children", None):
                for node in node["children"]:
                    print_node(node, depth + 1)

        nodes = SummaryText.get_assessment_descendants(assessment.id, json_encode=False)
        if nodes[0].get("children", None):
            for node in nodes[0]["children"]:
                print_node(node, 2)


class HeatmapDataset(PydanticModel):
    type: str
    name: str
    url: str


class HeatmapDatasets(PydanticModel):
    datasets: List[HeatmapDataset]


class Visual(models.Model):
    objects = managers.VisualManager()

    BIOASSAY_AGGREGATION = 0
    BIOASSAY_CROSSVIEW = 1
    ROB_HEATMAP = 2
    ROB_BARCHART = 3
    LITERATURE_TAGTREE = 4
    EXTERNAL_SITE = 5
    EXPLORE_HEATMAP = 6

    VISUAL_CHOICES = (
        (BIOASSAY_AGGREGATION, "animal bioassay endpoint aggregation"),
        (BIOASSAY_CROSSVIEW, "animal bioassay endpoint crossview"),
        (ROB_HEATMAP, "risk of bias heatmap"),
        (ROB_BARCHART, "risk of bias barchart"),
        (LITERATURE_TAGTREE, "literature tagtree"),
        (EXTERNAL_SITE, "embedded external website"),
        (EXPLORE_HEATMAP, "exploratory heatmap"),
    )

    SORT_ORDER_CHOICES = (
        ("short_citation", "Short Citation"),
        ("overall_confidence", "Final Study Confidence"),
    )

    title = models.CharField(max_length=128)
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used to describe this object "
        "(no spaces or special-characters).",
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="visuals")
    visual_type = models.PositiveSmallIntegerField(choices=VISUAL_CHOICES)
    dose_units = models.ForeignKey(DoseUnits, on_delete=models.SET_NULL, blank=True, null=True)
    prefilters = models.TextField(default="{}")
    endpoints = models.ManyToManyField(
        BaseEndpoint,
        related_name="visuals",
        help_text="Endpoints to be included in visualization",
        blank=True,
    )
    studies = models.ManyToManyField(
        Study,
        related_name="visuals",
        help_text="Studies to be included in visualization",
        blank=True,
    )
    settings = models.TextField(default="{}")
    caption = models.TextField(blank=True)
    published = models.BooleanField(
        default=False,
        verbose_name="Publish visual for public viewing",
        help_text="For assessments marked for public viewing, mark visual to be viewable by public",
    )
    sort_order = models.CharField(
        max_length=40, choices=SORT_ORDER_CHOICES, default="short_citation",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        unique_together = (("assessment", "slug"),)

    def __str__(self):
        return self.title

    @staticmethod
    def get_list_url(assessment_id):
        return reverse("summary:visualization_list", args=[str(assessment_id)])

    def get_absolute_url(self):
        return reverse("summary:visualization_detail", args=[str(self.pk)])

    def get_update_url(self):
        return reverse("summary:visualization_update", args=[str(self.pk)])

    def get_delete_url(self):
        return reverse("summary:visualization_delete", args=[str(self.pk)])

    def get_assessment(self):
        return self.assessment

    def get_api_detail(self):
        return reverse("summary:api:visual-detail", args=(self.id,))

    def get_api_heatmap_datasets(self):
        return reverse("summary:api:assessment-heatmap-datasets", args=(self.assessment_id,))

    @classmethod
    def get_heatmap_datasets(cls, assessment: Assessment) -> HeatmapDatasets:
        return HeatmapDatasets(
            datasets=[
                HeatmapDataset(
                    type="Literature",
                    name="Literature summary",
                    url=reverse("lit:api:assessment-tag-heatmap", args=(assessment.id,)),
                ),
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
                    url=reverse("animal:api:assessment-endpoint-heatmap", args=(assessment.id,)),
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
                *(
                    HeatmapDataset(
                        type="Dataset", name=f"Dataset: {ds.name}", url=ds.get_api_data_url()
                    )
                    for ds in assessment.datasets.all()
                ),
            ]
        )

    @staticmethod
    def get_dose_units():
        return DoseUnits.objects.json_all()

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def get_endpoints(self, request=None):
        qs = Endpoint.objects.none()
        filters = {"assessment_id": self.assessment_id}

        if self.visual_type == self.BIOASSAY_AGGREGATION:
            if request:
                ids = request.POST.getlist("endpoints")
            else:
                ids = self.endpoints.values_list("id", flat=True)

            filters["id__in"] = ids
            qs = Endpoint.objects.filter(**filters)

        elif self.visual_type == self.BIOASSAY_CROSSVIEW:

            if request:
                dose_id = tryParseInt(request.POST.get("dose_units"), -1)
                Prefilter.setFiltersFromForm(filters, request.POST, self.visual_type)

            else:
                dose_id = self.dose_units_id
                Prefilter.setFiltersFromObj(filters, self.prefilters)

            filters["animal_group__dosing_regime__doses__dose_units_id"] = dose_id
            qs = Endpoint.objects.filter(**filters).distinct("id")

        return qs

    def get_studies(self, request=None):
        """
        If there are endpoint-level prefilters, we get all studies which
        match this criteria. Otherwise, we use the M2M list of studies attached
        to the model.
        """
        qs = Study.objects.none()
        filters = {"assessment_id": self.assessment_id}

        if self.visual_type in [self.ROB_HEATMAP, self.ROB_BARCHART]:
            if request:
                efilters = {"assessment_id": self.assessment_id}
                Prefilter.setFiltersFromForm(efilters, request.POST, self.visual_type)
                if len(efilters) > 1:
                    filters["id__in"] = set(
                        Endpoint.objects.filter(**efilters).values_list(
                            "animal_group__experiment__study_id", flat=True
                        )
                    )
                else:
                    filters["id__in"] = request.POST.getlist("studies")

                qs = Study.objects.filter(**filters)

            else:
                if self.prefilters != "{}":
                    efilters = {"assessment_id": self.assessment_id}
                    Prefilter.setFiltersFromObj(efilters, self.prefilters)
                    filters["id__in"] = set(
                        Endpoint.objects.filter(**efilters).values_list(
                            "animal_group__experiment__study_id", flat=True
                        )
                    )
                    qs = Study.objects.filter(**filters)
                else:
                    qs = self.studies.all()

        if self.sort_order:
            if self.sort_order == "overall_confidence":
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

        data = {
            "assessment": self.assessment_id,
            "title": request.POST.get("title"),
            "slug": request.POST.get("slug"),
            "caption": request.POST.get("caption"),
            "dose_units": dose_units,
            "created": timezone.now().isoformat(),
            "last_updated": timezone.now().isoformat(),
        }

        data["endpoints"] = [
            SerializerHelper.get_serialized(e, json=False) for e in self.get_endpoints(request)
        ]

        data["studies"] = [
            SerializerHelper.get_serialized(s, json=False) for s in self.get_studies(request)
        ]

        return json.dumps(data)

    def copy_across_assessments(self, cw: Dict):
        old_id = self.id

        study_cw = cw[get_model_copy_name(Study)]
        new_study_ids = []
        for study in self.studies.all().order_by("id"):
            if study.id in study_cw:
                new_study_ids.append(study_cw[study.id])
            else:
                logger.warning(f"Study {study.id} ({study}) missing from viz: {self.id}")
        new_studies = list(Study.objects.filter(id__in=new_study_ids))
        assert len(new_study_ids) == len(new_studies)

        if self.endpoints.all().count() > 0:
            raise NotImplementedError("Requires implementation to copy this visual type")

        self.id = None
        self.assessment_id = cw[get_model_copy_name(self.assessment)][self.assessment_id]
        self.prefilters = Prefilter.copy_across_assessments(self.prefilters, cw)
        self.settings = self._update_settings_across_assessments(cw)
        self.save()

        # set m2m settings
        self.studies.set(new_studies)

        cw[get_model_copy_name(self)][old_id] = self.id

    def _update_settings_across_assessments(self, cw: Dict) -> str:
        settings = json.loads(self.settings)

        if (self.visual_type == 1) and "included_metrics" in settings:
            pass

        if (self.visual_type == 2 or self.visual_type == 3) and "included_metrics" in settings:
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
    settings = models.TextField(
        default="undefined",
        help_text="Paste content from a settings file from a different "
        'data-pivot, or keep set to "undefined".',
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

    @staticmethod
    def get_list_url(assessment_id):
        return reverse("summary:visualization_list", args=[str(assessment_id)])

    def get_absolute_url(self):
        return reverse("summary:dp_detail", kwargs={"pk": self.assessment_id, "slug": self.slug})

    def get_visualization_update_url(self):
        return reverse("summary:dp_update", kwargs={"pk": self.assessment_id, "slug": self.slug})

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

    def get_settings(self):
        try:
            return json.loads(self.settings)
        except ValueError:
            return None

    @staticmethod
    def reset_row_overrides(settings):
        settings_as_json = json.loads(settings)
        settings_as_json["row_overrides"] = []
        return json.dumps(settings_as_json)

    def copy_across_assessment(cw):
        raise NotImplementedError("Only implemented on child classes")


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

    def copy_across_assessments(self, cw):
        old_id = self.id
        new_assessment_id = cw[get_model_copy_name(self.assessment)][self.assessment_id]

        # copy base
        base = self.datapivot_ptr
        base.id = None
        base.assessment_id = new_assessment_id
        base.save()

        # copy self
        self.id = None
        self.assessment_id = new_assessment_id
        self.datapivot_ptr = base
        self.save()

        # TODO - check multitable inheritance
        # TODO - improve prefilters and setttings?

        cw[get_model_copy_name(self)][old_id] = self.id

    def _update_settings_across_assessments(self, cw: Dict) -> str:
        # no changes required
        return self.settings

    def get_dataset(self) -> FlatExport:
        worksheet_name = self.worksheet_name if len(self.worksheet_name) > 0 else 0
        df = read_excel(self.excel_file.file, sheet_name=worksheet_name)
        filename = os.path.splitext(os.path.basename(self.excel_file.file.name))[0]
        return FlatExport(df=df, filename=filename)


class DataPivotQuery(DataPivot):
    objects = managers.DataPivotQueryManager()

    MAXIMUM_QUERYSET_COUNT = 1000

    EXPORT_GROUP = 0
    EXPORT_ENDPOINT = 1
    EXPORT_STYLE_CHOICES = (
        (EXPORT_GROUP, "One row per Endpoint-group/Result-group"),
        (EXPORT_ENDPOINT, "One row per Endpoint/Result"),
    )

    evidence_type = models.PositiveSmallIntegerField(choices=STUDY_TYPE_CHOICES, default=BIOASSAY)
    export_style = models.PositiveSmallIntegerField(
        choices=EXPORT_STYLE_CHOICES,
        default=EXPORT_GROUP,
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
    prefilters = models.TextField(default="{}")
    published_only = models.BooleanField(
        default=True,
        verbose_name="Published studies only",
        help_text="Only present data from studies which have been marked as "
        '"published" in HAWC.',
    )

    def clean(self):
        count = self.get_queryset().count()

        if count == 0:
            err = """
                Current settings returned 0 results; make your filtering
                settings less restrictive (check units and/or prefilters).
            """
            raise ValidationError(err)

        if count > self.MAXIMUM_QUERYSET_COUNT:
            err = """
                Current settings returned too many results
                ({0} returned; a maximum of {1} are allowed);
                make your filtering settings more restrictive
                (check units and/or prefilters).
            """.format(
                count, self.MAXIMUM_QUERYSET_COUNT
            )
            raise ValidationError(err)

    def _get_dataset_filters(self):
        filters = {}

        if self.evidence_type == BIOASSAY:

            filters["assessment_id"] = self.assessment_id
            if self.published_only:
                filters["animal_group__experiment__study__published"] = True
            if self.preferred_units:
                filters["animal_group__dosing_regime__doses__dose_units__in"] = self.preferred_units

        elif self.evidence_type == EPI:

            filters["assessment_id"] = self.assessment_id
            if self.published_only:
                filters["study_population__study__published"] = True

        elif self.evidence_type == EPI_META:

            filters["protocol__study__assessment_id"] = self.assessment_id
            if self.published_only:
                filters["protocol__study__published"] = True

        elif self.evidence_type == IN_VITRO:

            filters["assessment_id"] = self.assessment_id
            if self.published_only:
                filters["experiment__study__published"] = True

        Prefilter.setFiltersFromObj(filters, self.prefilters)
        return filters

    def _get_dataset_queryset(self, filters):
        if self.evidence_type == BIOASSAY:
            qs = Endpoint.objects.filter(**filters)

        elif self.evidence_type == EPI:
            qs = Outcome.objects.filter(**filters)

        elif self.evidence_type == EPI_META:
            qs = MetaResult.objects.filter(**filters)

        elif self.evidence_type == IN_VITRO:
            qs = IVEndpoint.objects.filter(**filters)

        return qs.order_by("id")

    def _get_dataset_exporter(self, qs):
        if self.evidence_type == BIOASSAY:

            # select export class
            if self.export_style == self.EXPORT_GROUP:
                ExportClass = EndpointGroupFlatDataPivot
            elif self.export_style == self.EXPORT_ENDPOINT:
                ExportClass = EndpointFlatDataPivot

            exporter = ExportClass(
                qs,
                assessment=self.assessment,
                filename=f"{self.assessment}-animal-bioassay",
                preferred_units=self.preferred_units,
            )

        elif self.evidence_type == EPI:
            exporter = OutcomeDataPivot(
                qs, assessment=self.assessment, filename=f"{self.assessment}-epi",
            )

        elif self.evidence_type == EPI_META:
            exporter = MetaResultFlatDataPivot(
                qs, assessment=self.assessment, filename=f"{self.assessment}-epi",
            )

        elif self.evidence_type == IN_VITRO:

            # select export class
            if self.export_style == self.EXPORT_GROUP:
                Exporter = ivexports.DataPivotEndpointGroup
            elif self.export_style == self.EXPORT_ENDPOINT:
                Exporter = ivexports.DataPivotEndpoint

            # generate export
            exporter = Exporter(
                qs, assessment=self.assessment, filename=f"{self.assessment}-invitro",
            )

        return exporter

    def get_queryset(self):
        filters = self._get_dataset_filters()
        return self._get_dataset_queryset(filters)

    def get_dataset(self) -> FlatExport:
        qs = self.get_queryset()
        exporter = self._get_dataset_exporter(qs)
        return exporter.build_export()

    @property
    def visual_type(self):
        if self.evidence_type == BIOASSAY:
            return "Data pivot (animal bioassay)"
        elif self.evidence_type == EPI:
            return "Data pivot (epidemiology)"
        elif self.evidence_type == EPI_META:
            return "Data pivot (epidemiology meta-analysis/pooled-analysis)"
        elif self.evidence_type == IN_VITRO:
            return "Data pivot (in vitro)"
        else:
            raise ValueError("Unknown type")

    def copy_across_assessments(self, cw):
        old_id = self.id
        new_assessment_id = cw[get_model_copy_name(self.assessment)][self.assessment_id]

        # copy base
        base = self.datapivot_ptr
        base.id = None
        base.assessment_id = new_assessment_id
        base.save()

        # copy self
        self.id = None
        self.assessment_id = new_assessment_id
        self.datapivot_ptr = base
        self.prefilters = Prefilter.copy_across_assessments(self.prefilters, cw)
        self.save()

        cw[get_model_copy_name(self)][old_id] = self.id

    def _update_settings_across_assessments(self, cw: Dict) -> str:
        try:
            settings = json.loads(self.settings)
        except json.JSONDecodeError:
            return self.settings

        if len(settings["row_overrides"]) > 0:
            if self.evidence_type == BIOASSAY and self.export_style == self.EXPORT_GROUP:
                Model = apps.get_model("animal", "EndpointGroup")
            elif self.evidence_type == BIOASSAY and self.export_style == self.EXPORT_ENDPOINT:
                Model = apps.get_model("animal", "Endpoint")
            elif self.evidence_type == EPI and self.export_style == self.EXPORT_GROUP:
                Model = apps.get_model("epi", "ResultGroup")
            elif self.evidence_type == EPI and self.export_style == self.EXPORT_ENDPOINT:
                Model = apps.get_model("epi", "Outcome")
            else:
                raise NotImplementedError()

            model_cw = cw[get_model_copy_name(Model)]
            for override in settings["row_overrides"]:
                override.update(pk=model_cw[override["pk"]])

        return json.dumps(settings)


class Prefilter:
    """
    Helper-object to deal with DataPivot and Visual prefilters fields.
    """

    @staticmethod
    def setFiltersFromForm(filters, d, visual_type):
        evidence_type = d.get("evidence_type")

        if visual_type == Visual.BIOASSAY_CROSSVIEW:
            evidence_type = BIOASSAY

        if d.get("prefilter_system"):
            filters["system__in"] = d.getlist("systems")

        if d.get("prefilter_organ"):
            filters["organ__in"] = d.getlist("organs")

        if d.get("prefilter_effect"):
            filters["effect__in"] = d.getlist("effects")

        if d.get("prefilter_effect_subtype"):
            filters["effect_subtype__in"] = d.getlist("effect_subtypes")

        if d.get("prefilter_effect_tag"):
            filters["effects__in"] = d.getlist("effect_tags")

        if d.get("prefilter_episystem"):
            filters["system__in"] = d.getlist("episystems")

        if d.get("prefilter_epieffect"):
            filters["effect__in"] = d.getlist("epieffects")

        if d.get("prefilter_study"):
            studies = d.getlist("studies", [])
            if evidence_type == BIOASSAY:
                filters["animal_group__experiment__study__in"] = studies
            elif evidence_type == EPI:
                filters["study_population__study__in"] = studies
            elif evidence_type == IN_VITRO:
                filters["experiment__study__in"] = studies
            elif evidence_type == EPI_META:
                filters["protocol__study__in"] = studies
            else:
                raise ValueError("Unknown evidence type")

        if d.get("published_only"):
            if evidence_type == BIOASSAY:
                filters["animal_group__experiment__study__published"] = True
            elif evidence_type == EPI:
                filters["study_population__study__published"] = True
            elif evidence_type == IN_VITRO:
                filters["experiment__study__published"] = True
            elif evidence_type == EPI_META:
                filters["protocol__study__published"] = True
            else:
                raise ValueError("Unknown evidence type")

    @staticmethod
    def setFiltersFromObj(filters, prefilters):
        filters.update(json.loads(prefilters))

    @staticmethod
    def copy_across_assessments(prefilters: str, cw: Dict) -> str:
        filters = json.loads(prefilters)
        for study_id_key in [
            "animal_group__experiment__study__in",
            "study_population__study__in",
            "experiment__study__in",
            "protocol__study__in",
        ]:
            if study_id_key in filters:
                ids = []
                for id_ in filters[study_id_key]:
                    if int(id_) in cw[get_model_copy_name(Study)]:
                        ids.append(str(cw[get_model_copy_name(Study)][int(id_)]))
                filters[study_id_key] = ids
        return json.dumps(filters)


reversion.register(SummaryText)
reversion.register(DataPivotUpload)
reversion.register(DataPivotQuery)
reversion.register(Visual)
