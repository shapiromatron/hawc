from datetime import datetime
import json

from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

from comments.models import Comment
from utils.helper import HAWCDjangoJSONEncoder

import reversion
from treebeard.mp_tree import MP_Node

from utils.helper import HAWCdocx


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
        title = 'Summary Text: ' + HAWCdocx.to_date_string(datetime.now())
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


reversion.register(SummaryText)
