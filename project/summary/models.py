from datetime import datetime
import json

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

from assessment.models import Assessment, DoseUnits, BaseEndpoint
from study.models import Study
from animal.models import Endpoint
from epi.models import Outcome
from epimeta.models import MetaResult
from invitro.models import IVEndpoint

from animal.exports import EndpointGroupFlatDataPivot, EndpointFlatDataPivot
from epi.exports import OutcomeDataPivot
from epimeta.exports import MetaResultFlatDataPivot
import invitro.exports as ivexports

from reversion import revisions as reversion
from treebeard.mp_tree import MP_Node

from utils.helper import HAWCtoDateString, HAWCDjangoJSONEncoder, \
    SerializerHelper, tryParseInt

from . import managers

BIOASSAY = 0
EPI = 1
EPI_META = 4
IN_VITRO = 2
OTHER = 3

STUDY_TYPE_CHOICES = (
    (BIOASSAY, 'Animal Bioassay'),
    (EPI, 'Epidemiology'),
    (EPI_META, 'Epidemiology meta-analysis/pooled analysis'),
    (IN_VITRO, 'In vitro'),
    (OTHER, 'Other'))


class SummaryText(MP_Node):
    objects = managers.SummaryTextManager()

    assessment = models.ForeignKey(Assessment)
    title = models.CharField(max_length=128)
    slug = models.SlugField(verbose_name="URL Name",
                            help_text="The URL (web address) used on the website to describe this object (no spaces or special-characters).",
                            unique=True)
    text = models.TextField(default="")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Summary Text Descriptions"
        unique_together = (("assessment", "title"),
                           ("assessment", "slug"),)

    def __str__(self):
        return self.title

    @classmethod
    def assessment_qs(cls, assessment_id):
        return cls.objects.filter(assessment=assessment_id)

    @classmethod
    def get_assessment_root_node(cls, assessment_id):
        return SummaryText.objects.get(title='assessment-{}'.format(assessment_id))

    @classmethod
    def get_assessment_queryset(cls, assessment_id):
        return cls.get_assessment_root_node(assessment_id).get_descendants()

    @classmethod
    def build_default(cls, assessment):
        assessment = SummaryText.add_root(
            assessment=assessment,
            title='assessment-{pk}'.format(pk=assessment.pk),
            slug='assessment-{pk}-slug'.format(pk=assessment.pk),
            text="Root-level text")

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

    @classmethod
    def create(cls, form):
        instance = form.save(commit=False)
        sibling = form.cleaned_data.get('sibling')
        if sibling:
            return sibling.add_sibling(pos="right", instance=instance)
        else:
            parent = form.cleaned_data.get(
                'parent',
                SummaryText.get_assessment_root_node(instance.assessment.id)
            )
            sibling = parent.get_first_child()
            if sibling:
                return sibling.add_sibling(pos="first-sibling", instance=instance)
            else:
                return parent.add_child(instance=instance)

    def update(self, form):
        data = form.cleaned_data
        self.title = data['title']
        self.slug = data['slug']
        self.text = data['text']
        self.save()
        self.move_st(parent=data.get('parent'), sibling=data.get('sibling'))

    def move_st(self, parent=None, sibling=None):
        if parent is not None and parent.assessment != self.assessment:
            raise Exception("Parent assessment != self assessment")

        if sibling is not None and sibling.assessment != self.assessment:
            raise Exception("Sibling assessment != self assessment")

        if sibling:
            if self.get_prev_sibling() != sibling:
                self.move(sibling, pos='right')
        elif parent:
            self.move(parent, pos='first-child')

    def get_absolute_url(self):
        return '{url}#{id}'.format(url=reverse('summary:list', kwargs={'assessment': self.assessment.pk}),
                                   id=self.slug)

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_report(cls, report, assessment):
        title = 'Summary Text: ' + HAWCtoDateString(datetime.now())
        report.doc.add_heading(title, level=1)

        preface = 'Preliminary summary-text export in Word (work in progress)'
        p = report.doc.add_paragraph(preface)
        p.italic = True

        def print_node(node, depth):
            report.doc.add_heading(node['data']['title'], level=depth)
            report.doc.add_paragraph(strip_tags(node['data']['text']))
            if node.get('children', None):
                for node in node['children']:
                    print_node(node, depth+1)

        nodes = SummaryText.get_assessment_descendants(assessment.id, json_encode=False)
        if nodes[0].get('children', None):
            for node in nodes[0]['children']:
                print_node(node, 2)


class Visual(models.Model):
    objects = managers.VisualManager()

    BIOASSAY_AGGREGATION = 0
    BIOASSAY_CROSSVIEW = 1
    ROB_HEATMAP = 2
    ROB_BARCHART = 3

    VISUAL_CHOICES = (
        (BIOASSAY_AGGREGATION, "animal bioassay endpoint aggregation"),
        (BIOASSAY_CROSSVIEW, "animal bioassay endpoint crossview"),
        (ROB_HEATMAP, "risk of bias heatmap"),
        (ROB_BARCHART, "risk of bias barchart"), )

    title = models.CharField(
        max_length=128)
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used to describe this object "
                  "(no spaces or special-characters).")
    assessment = models.ForeignKey(
        Assessment,
        related_name='visuals')
    visual_type = models.PositiveSmallIntegerField(
        choices=VISUAL_CHOICES)
    dose_units = models.ForeignKey(
        DoseUnits,
        blank=True,
        null=True)
    prefilters = models.TextField(
        default="{}")
    endpoints = models.ManyToManyField(
        BaseEndpoint,
        related_name='visuals',
        help_text="Endpoints to be included in visualization",
        blank=True)
    studies = models.ManyToManyField(
        Study,
        related_name='visuals',
        help_text="Studies to be included in visualization",
        blank=True)
    settings = models.TextField(
        default="{}")
    caption = models.TextField(
        blank=True)
    published = models.BooleanField(
        default=False,
        verbose_name='Publish visual for public viewing',
        help_text='For assessments marked for public viewing, mark visual to be viewable by public')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = (("assessment", "slug"), )

    def __str__(self):
        return self.title

    @staticmethod
    def get_list_url(assessment_id):
        return reverse('summary:visualization_list', args=[str(assessment_id)])

    def get_absolute_url(self):
        return reverse('summary:visualization_detail', args=[str(self.pk)])

    def get_update_url(self):
        return reverse('summary:visualization_update', args=[str(self.pk)])

    def get_delete_url(self):
        return reverse('summary:visualization_delete', args=[str(self.pk)])

    def get_assessment(self):
        return self.assessment

    def get_endpoints(self, request=None):
        qs = Endpoint.objects.none()
        filters = {"assessment_id": self.assessment_id}

        if self.visual_type == self.BIOASSAY_AGGREGATION:
            if request:
                ids = request.POST.getlist('endpoints_1')
            else:
                ids = self.endpoints.values_list('id', flat=True)

            filters["id__in"] = ids
            qs = Endpoint.objects.filter(**filters)

        elif self.visual_type == self.BIOASSAY_CROSSVIEW:

            if request:
                dose_id = tryParseInt(request.POST.get('dose_units'), -1)
                Prefilter.setFiltersFromForm(filters, request.POST, self.visual_type)

            else:
                dose_id = self.dose_units_id
                Prefilter.setFiltersFromObj(filters, self.prefilters)

            filters["animal_group__dosing_regime__doses__dose_units_id"] = dose_id
            qs = Endpoint.objects.filter(**filters).distinct('id')

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
                        Endpoint.objects
                            .filter(**efilters)
                            .values_list('animal_group__experiment__study_id', flat=True))
                else:
                    filters["id__in"] = request.POST.getlist('studies')

                qs = Study.objects.filter(**filters)

            else:
                if self.prefilters != "{}":
                    efilters = {"assessment_id": self.assessment_id}
                    Prefilter.setFiltersFromObj(efilters, self.prefilters)
                    filters["id__in"] = set(
                        Endpoint.objects
                            .filter(**efilters)
                            .values_list('animal_group__experiment__study_id', flat=True))
                    qs = Study.objects.filter(**filters)
                else:
                    qs = self.studies.all()

        return qs

    def get_editing_dataset(self, request):
        # Generate a pseudo-return when editing or creating a dataset.
        # Do not include the settings field; this will be set from the
        # input-form. Should approximately mirror the Visual API from rest-framework.

        dose_units = None
        try:
            dose_units = int(request.POST.get("dose_units"))
        except (TypeError, ValueError) as e:
            # TypeError if dose_units is None; ValueError if dose_units is ""
            pass

        data = {
            "title": request.POST.get("title"),
            "slug": request.POST.get("slug"),
            "caption": request.POST.get("caption"),
            "dose_units": dose_units,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        data["endpoints"] = [
            SerializerHelper.get_serialized(e, json=False)
            for e in self.get_endpoints(request)
        ]

        data["studies"] = [
            SerializerHelper.get_serialized(s, json=False)
            for s in self.get_studies(request)
        ]

        return json.dumps(data)


class DataPivot(models.Model):
    objects = managers.DataPivotManager()

    assessment = models.ForeignKey(
        Assessment)
    title = models.CharField(
        max_length=128,
        help_text="Enter the title of the visualization (spaces and special-characters allowed).")
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used to describe this object "
                  "(no spaces or special-characters).")
    settings = models.TextField(
        default="undefined",
        help_text="Paste content from a settings file from a different "
                  "data-pivot, or keep set to \"undefined\".")
    caption = models.TextField(
        blank=True,
        default="")
    published = models.BooleanField(
        default=False,
        verbose_name='Publish visual for public viewing',
        help_text='For assessments marked for public viewing, mark visual to be viewable by public')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = (("assessment", "slug"), )
        ordering = ('title', )

    def __str__(self):
        return self.title

    @staticmethod
    def get_list_url(assessment_id):
        return reverse('summary:visualization_list', args=[str(assessment_id)])

    def get_absolute_url(self):
        return reverse(
            'summary:dp_detail',
            kwargs={'pk': self.assessment_id, 'slug': self.slug})

    def get_visualization_update_url(self):
        return reverse(
            'summary:dp_update',
            kwargs={'pk': self.assessment_id, 'slug': self.slug})

    def get_assessment(self):
        return self.assessment

    def get_download_url(self):
        # get download url for Excel file (default download-type)
        if hasattr(self, 'datapivotupload'):
            return self.datapivotupload.get_download_url()
        else:
            return self.datapivotquery.get_download_url()

    def get_data_url(self):
        # get download url for tab-separated values, used in data_pivot.js
        if hasattr(self, 'datapivotupload'):
            return self.datapivotupload.get_data_url()
        else:
            return self.datapivotquery.get_data_url()

    @property
    def visual_type(self):
        if hasattr(self, 'datapivotupload'):
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
        settings_as_json['row_overrides'] = []
        return json.dumps(settings_as_json)


class DataPivotUpload(DataPivot):
    objects = managers.DataPivotUploadManager()

    file = models.FileField(
        upload_to='data_pivot',
        help_text="The data should be in unicode-text format, tab delimited "
                  "(this is a standard output type in Microsoft Excel).")

    def get_data_url(self):
        return self.file.url

    def get_download_url(self):
        return self.file.url

    @property
    def visual_type(self):
        return "Data pivot (file upload)"


class DataPivotQuery(DataPivot):
    objects = managers.DataPivotQueryManager()

    MAXIMUM_QUERYSET_COUNT = 500

    EXPORT_GROUP = 0
    EXPORT_ENDPOINT = 1
    EXPORT_STYLE_CHOICES = (
        (EXPORT_GROUP, "One row per Endpoint-group/Result-group"),
        (EXPORT_ENDPOINT, "One row per Endpoint/Result"),
    )

    evidence_type = models.PositiveSmallIntegerField(
        choices=STUDY_TYPE_CHOICES,
        default=BIOASSAY)
    export_style = models.PositiveSmallIntegerField(
        choices=EXPORT_STYLE_CHOICES,
        default=EXPORT_GROUP,
        help_text="The export style changes the level at which the "
                  "data are aggregated, and therefore which columns and types "
                  "of data are presented in the export, for use in the visual.")
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
                  "creating one plot similar, but not identical, dose-units.")
    prefilters = models.TextField(
        default="{}")
    published_only = models.BooleanField(
        default=True,
        verbose_name="Published studies only",
        help_text='Only present data from studies which have been marked as '
                  '"published" in HAWC.')

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
            """.format(count, self.MAXIMUM_QUERYSET_COUNT)
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

        return qs

    def _get_dataset_exporter(self, qs, format_):
        if self.evidence_type == BIOASSAY:

            # select export class
            if self.export_style == self.EXPORT_GROUP:
                Exporter = EndpointGroupFlatDataPivot
            elif self.export_style == self.EXPORT_ENDPOINT:
                Exporter = EndpointFlatDataPivot

            exporter = Exporter(
                qs,
                export_format=format_,
                filename='{}-animal-bioassay'.format(self.assessment),
                preferred_units=self.preferred_units
            )

        elif self.evidence_type == EPI:
            exporter = OutcomeDataPivot(
                qs,
                export_format=format_,
                filename='{}-epi'.format(self.assessment)
            )

        elif self.evidence_type == EPI_META:
            exporter = MetaResultFlatDataPivot(
                qs,
                export_format=format_,
                filename='{}-epi-meta-analysis'.format(self.assessment)
            )

        elif self.evidence_type == IN_VITRO:

            # select export class
            if self.export_style == self.EXPORT_GROUP:
                Exporter = ivexports.DataPivotEndpointGroup
            elif self.export_style == self.EXPORT_ENDPOINT:
                Exporter = ivexports.DataPivotEndpoint

            # generate export
            exporter = Exporter(
                qs,
                export_format=format_,
                filename='{}-invitro'.format(self.assessment)
            )

        return exporter

    def get_queryset(self):
        filters = self._get_dataset_filters()
        return self._get_dataset_queryset(filters)

    def get_dataset(self, format_):
        qs = self.get_queryset()
        exporter = self._get_dataset_exporter(qs, format_)
        return exporter.build_response()

    def get_download_url(self):
        return reverse('summary:dp_data', kwargs={'pk': self.assessment_id, 'slug': self.slug})

    def get_data_url(self):
        return self.get_download_url() + "?format=tsv"

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


class Prefilter(object):
    """
    Helper-object to deal with DataPivot and Visual prefilters fields.
    """
    @staticmethod
    def setFiltersFromForm(filters, d, visual_type):
        evidence_type = d.get('evidence_type')

        if visual_type == Visual.BIOASSAY_CROSSVIEW:
            evidence_type = BIOASSAY

        if d.get('prefilter_system'):
            filters["system__in"] = d.getlist('systems')

        if d.get('prefilter_organ'):
            filters["organ__in"] = d.getlist('organs')

        if d.get('prefilter_effect'):
            filters["effect__in"] = d.getlist('effects')

        if d.get('prefilter_effect_tag'):
            filters["effects__in"] = d.getlist('effect_tags')

        if d.get('prefilter_episystem'):
            filters["system__in"] = d.getlist('episystems')

        if d.get('prefilter_epieffect'):
            filters["effect__in"] = d.getlist('epieffects')

        if d.get('prefilter_study'):
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


reversion.register(SummaryText)
reversion.register(DataPivotUpload)
reversion.register(DataPivotQuery)
reversion.register(Visual)
