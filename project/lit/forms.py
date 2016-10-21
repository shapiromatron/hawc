from cStringIO import StringIO
import logging
import numpy as np
import pandas as pd

from django.core.urlresolvers import reverse_lazy
from django import forms

from assessment.models import Assessment
from utils.forms import BaseFormHelper, addPopupLink

from litter_getter import ris

from . import models


class SearchForm(forms.ModelForm):

    title_str = 'Literature Search'
    help_text = ('Create a new literature search. Note that upon creation, '
                 'the search will not be executed, but can instead by run on '
                 'the next page. The search should be well-tested before '
                 'attempting to import into HAWC.')

    class Meta:
        model = models.Search
        fields = ('source', 'title', 'slug', 'description', 'search_string')

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(SearchForm, self).__init__(*args, **kwargs)
        self.instance.search_type = 's'
        if assessment:
            self.instance.assessment = assessment

        self.fields['source'].choices = [(1, 'PubMed')] # only current choice
        self.fields['description'].widget.attrs['rows'] = 3
        if 'search_string' in self.fields:
            self.fields['search_string'].widget.attrs['rows'] = 5
            self.fields['search_string'].required = True
        # by default take-up the whole row-fluid
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'

        self.helper = self.setHelper()

    def setHelper(self):
        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text":   u"Update an existing literature search",
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": u"Create new literature search",
                "help_text":   u"""
                    Create a new literature search. Note that upon creation,
                    the search will not be executed, but can instead by run on
                    the next page. The search should be well-tested before
                    attempting to import into HAWC.""",
                "cancel_url": reverse_lazy('lit:overview', kwargs={"pk": self.instance.assessment.pk})
            }

        helper = BaseFormHelper(self, **inputs)
        return helper


class ImportForm(SearchForm):

    def __init__(self, *args, **kwargs):
        super(ImportForm, self).__init__(*args, **kwargs)
        self.fields['source'].choices = [(1, 'PubMed'), (2, 'HERO')]
        self.fields['search_string'].help_text = "Enter a comma-separated list of database IDs for import."
        self.fields['search_string'].label = "ID List"
        self.instance.search_type = 'i'

        self.helper = self.setHelper()

    def setHelper(self):
        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text":   u"Update an existing literature search",
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": u"Create new literature import",
                "help_text":   u"""
                    Import a list of literature from an external database by
                    specifying a comma-separated list of primary keys from the
                    database. This is an import or known references, not a
                    search based on a query.""",
                "cancel_url": reverse_lazy('lit:overview', kwargs={"pk": self.instance.assessment.pk})
            }

        helper = BaseFormHelper(self, **inputs)
        return helper

    def clean_search_string(self):
        # make sure that it returns a list of positive unique integers
        valid_id = True
        ids = self.cleaned_data['search_string']
        vals = []
        for id in ids.split(','):
            try:
                val = int(id)
                if val < 0:
                    valid_id = False
                    break
                vals.append(val)
            except ValueError:
                valid_id = False
                break

        if len(vals) != len(set(vals)):
            raise forms.ValidationError("IDs must be unique.")

        if not valid_id:
            raise forms.ValidationError("Please enter a comma-separated list of numeric IDs.")

        return ids


class RISForm(SearchForm):

    def __init__(self, *args, **kwargs):
        super(RISForm, self).__init__(*args, **kwargs)
        self.fields['source'].choices = [(3, 'RIS (EndNote/Reference Manager)')]
        self.instance.search_type = 'i'
        self.fields['import_file'].required = True
        self.fields['import_file'].help_text = """Unicode RIS export file
            ({0} for EndNote library preparation)""".format(
            addPopupLink(reverse_lazy('lit:ris_export_instructions'), "view instructions"))

        self.helper = self.setHelper()

    def setHelper(self):
        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text":   u"Update an existing literature search",
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": u"Create new literature import",
                "help_text":   u"""
                    Import a list of literature from an RIS export; this is a
                    universal data-format which is used by reference management
                    software solutions such as EndNote or Reference Manager.
                """,
                "cancel_url": reverse_lazy('lit:overview', kwargs={"pk": self.instance.assessment.pk})
            }

        helper = BaseFormHelper(self, **inputs)
        return helper

    class Meta:
        model = models.Search
        fields = ('source', 'title', 'slug', 'description', 'import_file')

    def clean_import_file(self):
        fileObj = self.cleaned_data['import_file']
        if fileObj.size > 1024*1024*10:
            raise forms.ValidationError(
                'Input file must be <10 MB')
        if fileObj.name[-4:] not in (".txt", ".ris", ):
            raise forms.ValidationError(
                'File must have an ".ris" or ".txt" file-extension')
        if not ris.RisImporter.file_readable(fileObj):
            raise forms.ValidationError(
                'File cannot be successfully loaded. Are you sure this is a '
                'valid RIS file? If you are, please contact us and we will '
                'attempt to fix our import to ensure it works as expected.')
        return fileObj

    def clean(self):
        """
        In the clean-step, ensure RIS file is valid and references can be
        exported from file before save method. Cache the references on the
        instance method, so that upon import we don't need to re-read file.
        """
        cleaned_data = super(RISForm, self).clean()
        if not self._errors:
            # create a copy for RisImporter to open/close
            f = StringIO(cleaned_data['import_file'].read())
            importer = ris.RisImporter(f)
            self.instance._references = importer.references


class SearchModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} | {{{}}} | {}".format(obj.assessment, obj.get_search_type_display(), obj)


class SearchSelectorForm(forms.Form):

    searches = SearchModelChoiceField(queryset=models.Search.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        kwargs.pop('assessment', None)

        super(SearchSelectorForm, self).__init__(*args, **kwargs)

        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span11'

        assessment_pks = Assessment.objects.get_viewable_assessments(user)\
                                   .values_list('pk', flat=True)

        self.fields['searches'].queryset = self.fields['searches'].queryset\
                                               .filter(assessment__in=assessment_pks)\
                                               .exclude(title="Manual import")\
                                               .order_by('assessment_id')


class ReferenceForm(forms.ModelForm):

    class Meta:
        model = models.Reference
        fields = ('title', 'authors', 'year',
                  'journal', 'abstract', 'full_text_url', )

    def __init__(self, *args, **kwargs):
        super(ReferenceForm, self).__init__(*args, **kwargs)
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if fld in ['title', 'authors', 'journal']:
                widget.attrs['rows'] = 3

            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'

        inputs = {
            "legend_text": "Update reference details",
            "help_text":   """Update reference information which was fetched
                              from database or reference upload.""",
            "cancel_url": self.instance.get_absolute_url()
        }

        helper = BaseFormHelper(self, **inputs)
        helper.add_fluid_row('title', 2, "span6")
        helper.add_fluid_row('year', 2, "span6")
        helper.form_class = None
        return helper


class ReferenceFilterTagForm(forms.ModelForm):

    class Meta:
        model = models.ReferenceFilterTag
        fields = '__all__'


class ReferenceSearchForm(forms.Form):
    title = forms.CharField(
        required=False)
    authors = forms.CharField(
        required=False)
    journal = forms.CharField(
        required=False,
        help_text="Use shorthand name for journals.")
    db_id = forms.IntegerField(
        label='Database ID',
        help_text="Enter a PubMed or HERO database ID, for example 8675309",
        required=False)

    def __init__(self, *args, **kwargs):
        assessment_pk = kwargs.pop('assessment_pk', None)
        super(ReferenceSearchForm, self).__init__(*args, **kwargs)
        if assessment_pk:
            self.assessment = Assessment.objects.get(pk=assessment_pk)

    def search(self):
        """
        Returns a queryset of reference-search results.
        """
        query = {"assessment": self.assessment}
        if self.cleaned_data['title']:
            query['title__icontains'] = self.cleaned_data['title']
        if self.cleaned_data['authors']:
            query['authors__icontains'] = self.cleaned_data['authors']
        if self.cleaned_data['journal']:
            query['journal__icontains'] = self.cleaned_data['journal']
        if self.cleaned_data['db_id']:
            query['identifiers__unique_id'] = self.cleaned_data['db_id']

        refs = [
            r.get_json(json_encode=False, searches=True)
            for r in models.Reference.objects.filter(**query)
        ]

        return refs


class TagReferenceForm(forms.ModelForm):

    class Meta:
        model = models.Reference
        fields = ('tags',)


class TagsCopyForm(forms.Form):

    assessment = forms.ModelChoiceField(queryset=Assessment.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.assessment = kwargs.pop('assessment', None)
        super(TagsCopyForm, self).__init__(*args, **kwargs)
        self.fields['assessment'].widget.attrs['class'] = 'span12'
        self.fields['assessment'].queryset = Assessment.objects.get_viewable_assessments(
            user, exclusion_id=self.assessment.id)

    def copy_tags(self):
        models.ReferenceFilterTag.copy_tags(self.assessment, self.cleaned_data['assessment'])


class ReferenceExcelUploadForm(forms.Form):

    excel_file = forms.FileField(
        required=True,
        help_text='Upload an Excel file which contains at least two columns: '
                  'a "HAWC ID" column for the reference identifier, and a '
                  '"Full text URL" column which contains the URL for the '
                  'full text.')

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop('assessment')
        super(ReferenceExcelUploadForm, self).__init__(*args, **kwargs)
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = {
            "legend_text": "Upload full-text URLs",
            "help_text":   "Using an Excel file, upload full-text URLs "
                           "for multiple references",
            "cancel_url": reverse_lazy("lit:overview", args=[self.assessment.id])
        }
        helper = BaseFormHelper(self, **inputs)
        return helper

    def clean_excel_file(self):
        fn = self.cleaned_data['excel_file']
        if fn.name[-5:] not in ['.xlsx', '.xlsm'] and fn.name[-4:] not in ['.xls']:
            raise forms.ValidationError("Must be an Excel file with an "
                                        "extension xlsx, xlsm, or xls")

        try:
            df = pd.read_excel(fn.file)
            df = df[["HAWC ID", "Full text URL"]]
            df["Full text URL"].fillna("", inplace=True)
            assert df["HAWC ID"].dtype == np.int64
            assert df["Full text URL"].dtype == np.object0
            self.cleaned_data['df'] = df
        except Exception as e:
            logging.warning(e)
            raise forms.ValidationError(
                'Invalid Excel format. The first worksheet in the workbook '
                'must contain at least two columns -"HAWC ID", and '
                '"Full text URL"')
        return fn
