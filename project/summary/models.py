from datetime import datetime
import json

from django.db import models
from django.db.models.loading import get_model
from django.core.exceptions import ValidationError
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

from comments.models import Comment
from study.models import Study

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
        (1, "animal bioassay endpoint crossview"), )

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
    endpoints = models.ManyToManyField(
        'assessment.BaseEndpoint',
        related_name='visuals',
        help_text="Endpoints to be included in visualization",
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
        unique_together = (("assessment", "title"),
                           ("assessment", "slug"))

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('summary:visualization_detail', args=[str(self.pk)])

    def get_assessment(self):
        return self.assessment

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode, from_cache=False)

    def get_endpoints(self):
        qs = self.__class__.objects.none()
        if self.visual_type==0:
            qs = self.endpoints.all()
        elif self.visual_type==1:
            Endpoint = get_model('animal', 'Endpoint')
            qs = Endpoint.objects.filter(
                assessment_id=self.assessment_id,
                animal_group__dosing_regime__doses__dose_units_id=self.dose_units_id
            ).distinct('pk')
        return qs


class DataPivot(models.Model):
    assessment = models.ForeignKey(
        'assessment.assessment')
    title = models.CharField(
        max_length=128)
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
        unique_together = (("assessment", "title"),
                           ("assessment", "slug"))
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('summary:dp_detail', kwargs={'pk': self.assessment.pk,
                                                    'slug': self.slug})
    def get_assessment(self):
        return self.assessment

    def clean(self):
        # unique_together constraint checked above; not done in form because assessment is excluded
        pk_exclusion = {}
        if self.pk:
            pk_exclusion['pk'] = self.pk
        if DataPivot.objects.filter(assessment=self.assessment,
                                    title=self.title).exclude(**pk_exclusion).count() > 0:
            raise ValidationError('Error- title must be unique for assessment.')
        if DataPivot.objects.filter(assessment=self.assessment,
                                    slug=self.slug).exclude(**pk_exclusion).count() > 0:
            raise ValidationError('Error- slug name must be unique for assessment.')

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'title', 'caption')
        for field in fields:
            d[field] = getattr(self, field)

        d['settings'] = self.settings
        d['url'] = self.get_absolute_url()
        d['data_url'] = self.get_data_url()
        d['download_url'] = self.get_download_url()

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

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


class DataPivotUpload(DataPivot):
    file = models.FileField(
        upload_to='data_pivot',
        help_text="The data should be in unicode-text format, tab delimited "
                  "(this is a standard output type in Microsoft Excel).")

    def get_data_url(self):
        return self.file.url

    def get_download_url(self):
        return self.file.url


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

    def get_data_url(self):
        # request a tsv instead of Excel default
        url = self.get_download_url()
        if url.find("?")>=0:
            url += "&output=tsv"
        else:
            url += "?output=tsv"
        return url

    def get_download_url(self):
        # request an Excel file for download
        url = None
        if self.evidence_type == 0:  # Animal Bioassay:
            url = reverse('animal:endpoints_flatfile', kwargs={'pk': self.assessment.pk})
            if self.units:
                url += '?dose_pk={0}'.format(self.units.pk)
        elif self.evidence_type == 1:  # Epidemiology
            url = reverse('epi:ao_flat', kwargs={'pk': self.assessment.pk})
        elif self.evidence_type == 4:  # Epidemiology meta-analysis/pooled analysis
            url = reverse('epi:mr_flat', kwargs={'pk': self.assessment.pk})
        elif self.evidence_type == 2:  # In Vitro
            url = reverse('invitro:endpoints_flat', kwargs={'pk': self.assessment.pk})
        if url is None:
            raise Http404

        return url


reversion.register(SummaryText)
reversion.register(DataPivotUpload)
reversion.register(DataPivotQuery)
reversion.register(Visual)
