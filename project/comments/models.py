import json

from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from reversion import revisions as reversion

from myuser.models import HAWCUser
from utils.helper import HAWCDjangoJSONEncoder


class CommentSettings(models.Model):
    assessment = models.OneToOneField('assessment.Assessment',
                                      related_name='comment_settings',
                                      primary_key=True)
    allow_comments = models.BooleanField(default=False,
        help_text="All logged-in users with access to the assessment will be " +
                  "able to provide comments on key assessment components,  " +
                  "including study-quality, endpoints, and summary-text.  " +
                  "Anonymous comments cannot be provided.")
    public_comments = models.BooleanField(default=False,
        help_text="Any comments made will be viewable by anyone with access " +
                  "to the assessment. Associated responses to comments will also " +
                  "be presented. ")

    def get_assessment(self):
        return self.assessment

    def get_absolute_url(self):
        return reverse('comments:comment_settings_details',
                       args=[str(self.pk)])


COMMENT_MODEL_CROSSWALK = {
    "assessment": {"app_label": "assessment", "model": "assessment"},
    "study":      {"app_label": "study", "model": "study"},
    "experiment": {"app_label": "animal", "model": "experiment"},
    "animal_group": {"app_label": "animal", "model": "animalgroup"},
    "endpoint":     {"app_label": "animal", "model": "endpoint"},
    "reference_value": {"app_label": "animal", "model": "referencevalue"},
    "summary_text": {"app_label": "summary", "model": "summarytext"}}


class Comment(models.Model):
    assessment = models.ForeignKey('assessment.Assessment')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    commenter = models.ForeignKey(HAWCUser, related_name='commenters')
    title = models.CharField(max_length=256)
    text = models.TextField()
    slug = models.SlugField(verbose_name="URL Name",
                            help_text="The URL (web address) used to describe this object (no spaces or special-characters).")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    @staticmethod
    def get_content_object_type(content_type):
        match = COMMENT_MODEL_CROSSWALK.get(content_type, {"app_label": None, "model": None})
        return ContentType.objects.get(**match)

    @staticmethod
    def get_jsons(queryset, json_encode=True):
        lst = [obj.get_json(json_encode=False) for obj in queryset]
        if json_encode:
            return json.dumps(lst, cls=HAWCDjangoJSONEncoder)
        else:
            return lst

    def get_json(self, json_encode=True):
        d = {'commenter': self.commenter.get_full_name(), 'commenter_pk': self.commenter.pk}
        fields = ['pk', 'title', 'text', 'slug', 'created', 'last_updated']
        for field in fields:
            d[field] = getattr(self, field)

        d['parent_object']={'name':'', 'pk':'', 'url':'', 'type':''}
        try:
            d['parent_object']['name'] = self.content_object.__unicode__()
            d['parent_object']['pk'] = self.content_object.pk
            d['parent_object']['url'] = self.content_object.get_absolute_url()
            d['parent_object']['type'] = self.content_object._meta.object_name
        except:
            pass

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    def clean(self):
        if not self.assessment.comment_settings.allow_comments:
            raise ValidationError("Error- commenting not enabled for this assessment")
        if not self.assessment.user_can_view_object(self.commenter):
            raise ValidationError("Error- commenting not allowed for this user, for this assessment")

reversion.register(Comment)
