from django.core.urlresolvers import reverse_lazy
from django import forms

from assessment.models import Assessment
from utils.forms import BaseFormHelper

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
        self.fields['search_string'].widget.attrs['rows'] = 5
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

        if valid_id == False:
            raise forms.ValidationError("Please enter a comma-separated list of numeric IDs.")

        return ids


class SearchModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return "{} | {{{}}} | {}".format(obj.assessment, obj.get_search_type_display(), obj)


class SearchSelectorForm(forms.Form):

    searches = SearchModelChoiceField(queryset=models.Search.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        assessment = kwargs.pop('assessment', None)

        super(SearchSelectorForm, self).__init__(*args, **kwargs)

        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span11'

        assessment_pks = Assessment.get_viewable_assessments(user)\
                                   .values_list('pk', flat=True)

        self.fields['searches'].queryset = self.fields['searches'].queryset\
                                               .filter(assessment__in=assessment_pks)\
                                               .exclude(title="Manual import")\
                                               .order_by('assessment_id')


class ReferenceForm(forms.ModelForm):

    class Meta:
        model = models.Reference
        fields = ('tags',)


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
            r.get_json(json_encode=False)
            for r in models.Reference.objects.filter(**query)
        ]
        return refs


class TagsCopyForm(forms.Form):

    assessment = forms.ModelChoiceField(queryset=Assessment.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.assessment = kwargs.pop('assessment', None)
        super(TagsCopyForm, self).__init__(*args, **kwargs)
        self.fields['assessment'].widget.attrs['class'] = 'span12'
        self.fields['assessment'].queryset = Assessment.get_viewable_assessments(
            user, exclusion_id=self.assessment.id)

    def copy_tags(self):
        models.ReferenceFilterTag.copy_tags(self.assessment, self.cleaned_data['assessment'])


class NullForm(forms.Form):

    def __init__(self, *args, **kwargs):
        pass
