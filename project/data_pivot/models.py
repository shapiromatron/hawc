import json

from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import Http404

import reversion

from study.models import STUDY_TYPE_CHOICES
from utils.helper import HAWCDjangoJSONEncoder


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
    updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = (("assessment", "title"),
                           ("assessment", "slug"))
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('data_pivot:detail', kwargs={'pk': self.assessment.pk,
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
        choices=STUDY_TYPE_CHOICES,
        default=0)
    units = models.ForeignKey(
        'animal.doseunits')

    def get_data_url(self):
        # request a tsv instead of Excel default
        url = self.get_download_url()
        if self.evidence_type == 0:  # Animal Bioassay:
            return url + "&output=tsv"
        else:
            return url + "?output=tsv"

    def get_download_url(self):
        # request an Excel file for download
        url = None
        if self.evidence_type == 0:  # Animal Bioassay:
            url = reverse('animal:endpoints_flatfile', kwargs={'pk': self.assessment.pk}) + \
                          '?dose_pk={dpk}'.format(dpk=self.datapivotquery.units.pk)
        elif self.evidence_type == 1:  # Epidemiology
            url = reverse('epi:ao_flat', kwargs={'pk': self.assessment.pk})
        elif self.evidence_type == 2:  # In Vitro
            url = reverse('invitro:endpoints_flat', kwargs={'pk': self.assessment.pk})

        if url is None:
            raise Http404

        return url


reversion.register(DataPivotUpload)
reversion.register(DataPivotQuery)
