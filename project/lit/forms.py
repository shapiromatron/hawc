from django import forms

from assessment.models import Assessment

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
        self.fields['source'].choices = [(1, 'PubMed')] # only current choice
        self.fields['description'].widget.attrs['rows'] = 3
        self.fields['search_string'].widget.attrs['rows'] = 5
        self.instance.search_type = 's'
        if assessment:
            self.instance.assessment = assessment


class ImportForm(SearchForm):

    title_str = 'Literature Import'
    help_text = ('Create a new literature import. This will attempt to '
                 'interact with an external database, and will import a '
                 'specific subset of literature identified by primary keys '
                 'specified by the user. Thus, this is an import or known '
                 'references, not a search.')

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(ImportForm, self).__init__(*args, **kwargs)
        self.fields['source'].choices = [(1, 'PubMed'), (2, 'HERO')]
        self.fields['search_string'].help_text = "Enter a comma-separated list of database IDs for import."
        self.fields['search_string'].label = "ID List"
        self.fields['description'].widget.attrs['rows'] = 3
        self.fields['search_string'].widget.attrs['rows'] = 5
        self.instance.search_type = 'i'
        if assessment:
            self.instance.assessment = assessment


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

        assessment_pks = assessment.get_viewable_assessments(user=user, include_self=True)\
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


class ReferenceSearchForm(forms.Form):
    title = forms.CharField(required=False)
    authors = forms.CharField(required=False)
    journal = forms.CharField(required=False,
                              help_text="Use shorthand name for journals.")

    def __init__(self, *args, **kwargs):
        assessment_pk = kwargs.pop('assessment_pk', None)
        super(ReferenceSearchForm, self).__init__(*args, **kwargs)
        if assessment_pk:
            self.assessment = Assessment.objects.get(pk=assessment_pk)

    def search(self):
        """
        Returns a queryset of reference-search results.
        """
        query = {}
        if self.cleaned_data['title']:
            query['title__icontains'] = self.cleaned_data['title']
        if self.cleaned_data['authors']:
            query['authors__icontains'] = self.cleaned_data['authors']
        if self.cleaned_data['journal']:
            query['journal__icontains'] = self.cleaned_data['journal']

        refs_json = []
        for ref in models.Reference.objects.filter(assessment=self.assessment).filter(**query):
            refs_json.append(ref.get_json(json_encode=False))
        return refs_json


class TagsCopyForm(forms.Form):

    assessment = forms.ModelChoiceField(queryset=Assessment.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.assessment = kwargs.pop('assessment', None)
        super(TagsCopyForm, self).__init__(*args, **kwargs)
        self.fields['assessment'].widget.attrs['class'] = 'span12'
        self.fields['assessment'].queryset = self.assessment.get_viewable_assessments(user=user, include_self=False)

    def copy_tags(self):
        models.ReferenceFilterTag.copy_tags(self.assessment, self.cleaned_data['assessment'])
