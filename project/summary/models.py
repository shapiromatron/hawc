from datetime import datetime
import json

from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

from study.models import Study
from animal.models import Endpoint
from epi.models import AssessedOutcome, MetaResult
from invitro.models import IVEndpoint
from comments.models import Comment

from animal.exports import EndpointFlatDataPivot
from epi.exports import AssessedOutcomeFlatDataPivot, MetaResultFlatDataPivot
from invitro.exports import IVEndpointFlatDataPivot

import reversion
from treebeard.mp_tree import MP_Node

from utils.helper import HAWCtoDateString, HAWCDjangoJSONEncoder, SerializerHelper


class SummaryText(MP_Node):
    assessment = models.ForeignKey('assessment.Assessment')
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

    def __unicode__(self):
        return self.title

    @classmethod
    def get_assessment_root_node(cls, assessment):
        return SummaryText.objects.get(title='assessment-{pk}'.format(pk=assessment.pk))

    @classmethod
    def build_default(cls, assessment):
        assessment = SummaryText.add_root(
                       assessment=assessment,
                       title='assessment-{pk}'.format(pk=assessment.pk),
                       slug='assessment-{pk}-slug'.format(pk=assessment.pk),
                       text="Root-level text")

    @classmethod
    def get_all_tags(cls, assessment, json_encode=True):
        root = SummaryText.objects.get(title='assessment-{pk}'.format(pk=assessment.pk))
        tags = SummaryText.dump_bulk(root)

        if root.assessment.comment_settings.public_comments:
            descendants=root.get_descendants()
            obj_type = Comment.get_content_object_type('summary_text')
            comments=Comment.objects.filter(content_type=obj_type,
                                            object_id__in=descendants)
            tags[0]['data']['comments'] = Comment.get_jsons(comments, json_encode=False)

        if json_encode:
            return json.dumps(tags, cls=HAWCDjangoJSONEncoder)
        else:
            return tags

    @classmethod
    def add_summarytext(cls, **kwargs):
        for k, v in kwargs.iteritems():
            if type(kwargs[k]) == list:
                kwargs[k] = v[0]

        parent = kwargs.pop('parent', None)
        sibling = kwargs.pop('sibling', None)
        assessment = kwargs.get('assessment', None)
        if parent:
            if parent.assessment != assessment:
                raise Exception("Parent node assessment not for selected assessment")
            # left-most parent node
            if parent.get_children_count()>0:
                sibling = parent.get_first_child()
                return sibling.add_sibling(pos="first-sibling", **kwargs)
            else:
                return parent.add_child(**kwargs)
        elif sibling:
            # right of sibling
            if sibling.assessment != assessment:
                raise Exception("Sibling node assessment not for selected assessment")
            return sibling.add_sibling(pos="right", **kwargs)
        else:
            # right-most of assessment root
            parent = SummaryText.get_assessment_root_node(assessment)
            return parent.add_child(**kwargs)

    def modify(self, **kwargs):
        self.title = kwargs['title'][0]
        self.slug = kwargs['slug'][0]
        self.text = kwargs['text'][0]
        self.save()
        self.move_summarytext(parent=kwargs.get('parent', [None])[0],
                              sibling=kwargs.get('sibling', [None])[0])

    def move_summarytext(self, parent, sibling):
        if parent and sibling:
            return Exception("Should only specify one argument")
        if parent:
            # left-most child of parent node
            if parent.assessment != self.assessment:
                raise Exception("Parent node assessment not for selected assessment")
            if self.get_parent() != parent:
                self.move(parent, pos='first-child')
        elif sibling:
            # move self to right of sibling (position is counterintuitive)
            if sibling.assessment != self.assessment:
                raise Exception("Sibling node assessment not for selected assessment")
            if self.get_prev_sibling() != sibling:
                self.move(sibling, pos='left')

    def clean(self):
        # unique_together constraint checked above; not done in form because assessment is excluded
        pk_exclusion = {}
        if self.pk:
            pk_exclusion['pk'] = self.pk
        if SummaryText.objects.filter(assessment=self.assessment,
                                      title=self.title).exclude(**pk_exclusion).count() > 0:
            raise ValidationError('Error- title must be unique for assessment.')
        if SummaryText.objects.filter(assessment=self.assessment,
                                      slug=self.slug).exclude(**pk_exclusion).count() > 0:
            raise ValidationError('Error- slug name must be unique for assessment.')

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

        nodes = SummaryText.get_all_tags(assessment, json_encode=False)
        if nodes[0].get('children', None):
            for node in nodes[0]['children']:
                print_node(node, 2)


class Visual(models.Model):

    VISUAL_CHOICES = (
        (0, "animal bioassay endpoint aggregation"),
        (1, "animal bioassay endpoint crossview"),
        (2, "risk of bias heatmap"),
        (3, "risk of bias barchart"), )

    title = models.CharField(
        max_length=128)
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used to describe this object "
                  "(no spaces or special-characters).")
    assessment = models.ForeignKey(
        'assessment.Assessment',
        related_name='visuals')
    visual_type = models.PositiveSmallIntegerField(
        choices=VISUAL_CHOICES)
    dose_units = models.ForeignKey(
        'animal.DoseUnits',
        blank=True,
        null=True)
    prefilters = models.TextField(
        default="{}")
    endpoints = models.ManyToManyField(
        'assessment.BaseEndpoint',
        related_name='visuals',
        help_text="Endpoints to be included in visualization",
        blank=True,
        null=True)
    studies = models.ManyToManyField(
        Study,
        related_name='visuals',
        help_text="Studies to be included in visualization",
        blank=True,
        null=True)
    settings = models.TextField(
        default="{}")
    caption = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = (("assessment", "slug"), )

    def __unicode__(self):
        return self.title

    @classmethod
    def get_list_url(cls, assessment_id):
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

        if self.visual_type==0:
            if request:
                ids = request.POST.getlist('endpoints_1')
            else:
                ids = self.endpoints.values_list('id', flat=True)

            filters["id__in"] = ids
            qs = Endpoint.objects.filter(**filters)

        elif self.visual_type==1:
            if request:
                try:
                    dose_id = int(request.POST.get('dose_units', -1))
                except ValueError:
                    dose_id = -1
                Prefilter.setRequestFilters(filters, request=request)

            else:
                dose_id = self.dose_units_id
                Prefilter.setRequestFilters(filters, prefilters=self.prefilters)

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

        if self.visual_type in [2, 3]:
            if request:
                efilters = {"assessment_id": self.assessment_id}
                Prefilter.setRequestFilters(efilters, request=request)
                if len(efilters)>1:
                    filters["id__in"] = set(
                        Endpoint.objects\
                            .filter(**efilters)\
                            .values_list('animal_group__experiment__study_id', flat=True))
                else:
                    filters["id__in"] = request.POST.getlist('studies')

                qs = Study.objects.filter(**filters)

            else:
                if self.prefilters != "{}":
                    efilters = {"assessment_id": self.assessment_id}
                    Prefilter.setRequestFilters(efilters, prefilters=self.prefilters)
                    filters["id__in"] = set(
                        Endpoint.objects\
                            .filter(**efilters)\
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
    assessment = models.ForeignKey(
        'assessment.assessment')
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
        default="")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = (("assessment", "slug"), )
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    @classmethod
    def get_list_url(cls, assessment_id):
        return reverse('summary:visualization_list', args=[str(assessment_id)])

    def get_absolute_url(self):
        return reverse('summary:dp_detail', kwargs={'pk': self.assessment_id,
                                                    'slug': self.slug})

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


class DataPivotUpload(DataPivot):
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
    evidence_type = models.PositiveSmallIntegerField(
        choices=Study.STUDY_TYPE_CHOICES,
        default=0)
    units = models.ForeignKey(
        'animal.doseunits',
        blank=True,
        null=True,
        help_text="If kept-blank, dose-units will be random for each "
                  "endpoint presented. This setting may used for comparing "
                  "percent-response, where dose-units are not needed.")
    prefilters = models.TextField(
        default="{}")
    published_only = models.BooleanField(
        default=True,
        verbose_name="Published studies only",
        help_text='Only present data from studies which have been marked as '
                  '"published" in HAWC.')

    def _get_dataset_filters(self):
        filters = {}

        if self.evidence_type == 0:  # Animal Bioassay:

            filters["assessment_id"] = self.assessment_id
            if self.published_only:
                filters["animal_group__experiment__study__published"] = True
            if self.units_id:
                filters["animal_group__dosing_regime__doses__dose_units"] = self.units_id
            Prefilter.setRequestFilters(filters, prefilters=self.prefilters)

        elif self.evidence_type == 1:  # Epidemiology

            filters["assessment_id"] = self.assessment_id
            if self.published_only:
                filters["exposure__study_population__study__published"] = True

        elif self.evidence_type == 4:  # Epidemiology meta-analysis/pooled analysis

            filters["protocol__study__assessment_id"] = self.assessment_id
            if self.published_only:
                filters["protocol__study__published"] = True

        elif self.evidence_type == 2:  # In Vitro

            filters["assessment_id"] = self.assessment_id
            if self.published_only:
                filters["experiment__study__published"] = True

        return filters

    def _get_dataset_queryset(self, filters):
        if self.evidence_type == 0:  # Animal Bioassay:
            qs = Endpoint.objects.filter(**filters).distinct('pk')

        elif self.evidence_type == 1:  # Epidemiology
            qs = AssessedOutcome.objects.filter(**filters)

        elif self.evidence_type == 4:  # Epidemiology meta-analysis/pooled analysis
            qs = MetaResult.objects.filter(**filters)

        elif self.evidence_type == 2:  # In Vitro
            qs = IVEndpoint.objects.filter(**filters)

        return qs

    def _get_dataset_exporter(self, qs, format_):
        if self.evidence_type == 0:  # Animal Bioassay:
            exporter = EndpointFlatDataPivot(
                qs,
                export_format=format_,
                filename='{}-animal-bioassay'.format(self.assessment),
                dose=self.units
            )

        elif self.evidence_type == 1:  # Epidemiology
            exporter = AssessedOutcomeFlatDataPivot(
                qs,
                export_format=format_,
                filename='{}-epi'.format(self.assessment)
            )

        elif self.evidence_type == 4:  # Epidemiology meta-analysis/pooled analysis
            exporter = MetaResultFlatDataPivot(
                qs,
                export_format=format_,
                filename='{}-epi-meta-analysis'.format(self.assessment)
            )

        elif self.evidence_type == 2:  # In Vitro
            exporter = IVEndpointFlatDataPivot(
                qs,
                export_format=format_,
                filename='{}-invitro'.format(self.assessment)
            )

        return exporter

    def get_dataset(self, format_):
        filters = self._get_dataset_filters()
        qs = self._get_dataset_queryset(filters)
        exporter = self._get_dataset_exporter(qs, format_)
        return exporter.build_response()

    def get_download_url(self):
        return reverse('summary:dp_data', kwargs={'pk': self.assessment_id, 'slug': self.slug})

    def get_data_url(self):
        return self.get_download_url() + "?format=tsv"

    @property
    def visual_type(self):
        if self.evidence_type == 0:  # Animal Bioassay:
            return "Data pivot (animal bioassay)"
        elif self.evidence_type == 1:  # Epidemiology
            return "Data pivot (epidemiology)"
        elif self.evidence_type == 4:  # Epidemiology meta-analysis/pooled analysis
            return "Data pivot (epidemiology meta-analysis/pooled-analysis)"
        elif self.evidence_type == 2:  # In Vitro
            return "Data pivot (in vitro)"
        else:
            raise ValueError("Unknown type")


class Prefilter(object):
    """
    Helper-object to deal with DataPivot and Visual prefilters fields.
    TODO: override TextField and add methods
    """
    def __init__(self, form):
        self.form = form

    @classmethod
    def setRequestFilters(cls, filters, request=None, prefilters=None):
        if request:
            if request.POST.get('prefilter_system'):
                filters["system__in"] = request.POST.getlist('systems')

            if request.POST.get('prefilter_effect'):
                filters["effect__in"] = request.POST.getlist('effects')

            if request.POST.get("published_only"):
                filters["animal_group__experiment__study__published"] = True

        if prefilters:
            filters.update(json.loads(prefilters))

    def getFormName(self):
        return self.form.__class__.__name__

    def setInitialForm(self):
        prefilters = json.loads(self.form.instance.prefilters)
        for k,v in prefilters.iteritems():
            if k == "system__in":
                self.form.fields["systems"].initial = v
                self.form.fields["prefilter_system"].initial = True

            if k == "effect__in":
                self.form.fields["effects"].initial = v
                self.form.fields["prefilter_effect"].initial = True

        if self.getFormName() == "CrossviewForm":
            published_only = prefilters.get("animal_group__experiment__study__published", False)
            if self.form.instance.id is None:
                published_only = True
            self.form.fields["published_only"].initial = published_only

    def setPrefilters(self, data):
        prefilters = {}

        if data['prefilter_system']:
            prefilters["system__in"] = data.get("systems", [])

        if data['prefilter_effect']:
            prefilters["effect__in"] = data.get("effects", [])

        if self.getFormName() == "CrossviewForm" and data['published_only']:
            prefilters["animal_group__experiment__study__published"] = True

        return json.dumps(prefilters)

    def getChoices(self, field_name):
        assessment_id = self.form.instance.assessment_id
        choices = None

        if field_name == "systems":
            choices = list(Endpoint.get_system_choices(assessment_id))
        elif field_name == "effects":
            choices = list(Endpoint.get_effect_choices(assessment_id))
        else:
            raise ValueError("Unknown field name: {}".format(field_name))

        return choices


reversion.register(SummaryText)
reversion.register(DataPivotUpload)
reversion.register(DataPivotQuery)
reversion.register(Visual)
