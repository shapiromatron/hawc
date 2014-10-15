from django import forms

from assessment.models import Assessment

from . import models


class CommentForm(forms.ModelForm):

    class Meta:
        model = models.Comment
        fields = ('title', 'text')

    def __init__(self, *args, **kwargs):
        content_type = kwargs.pop('content_type', '')
        object_id = kwargs.pop('object_id', '')
        slug = kwargs.pop('slug', '')
        commenter = kwargs.pop('commenter')
        super(CommentForm, self).__init__(*args, **kwargs)
        self.instance.content_type = models.Comment.get_content_object_type(content_type)
        self.instance.object_id = object_id
        self.instance.slug = slug
        self.instance.commenter = commenter
        self.instance.assessment = self.instance.content_object.get_assessment()


class CommentSettingsForm(forms.ModelForm):

    class Meta:
        model = models.CommentSettings
        fields = ('allow_comments', 'public_comments', )

    def __init__(self, *args, **kwargs):
        assessment_pk = kwargs.pop('assessment_pk', None)
        super(CommentSettingsForm, self).__init__(*args, **kwargs)
        if assessment_pk:
            self.instance.assessment = Assessment.objects.get(pk=assessment_pk)
