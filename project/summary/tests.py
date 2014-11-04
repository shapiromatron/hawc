import re
import json
import pprint

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from assessment.tests import build_assessments_for_permissions_testing
from utils.helper import HAWCDjangoJSONEncoder

from .models import SummaryText

class SummaryTextTests(TestCase):
    def setUp(self):
        build_assessments_for_permissions_testing(self)

    @staticmethod
    def clean_json(json_dump):
        remove_fields = ['created', 'last_updated', 'slug', 'text', 'assessment']
        for node in json_dump:
            node.pop('id')
            for field in remove_fields:
                node['data'].pop(field)
            if node.get('children'):
                SummaryTextTests.clean_json(node['children'])


    def test_adding_texts(self):
        lvl_1a = SummaryText.add_summarytext(assessment=self.assessment_working,
                                             title='lvl_1a',
                                             slug='lvl_1a',
                                             text='text')

        lvl_1b = SummaryText.add_summarytext(assessment=self.assessment_working,
                                             title='lvl_1b',
                                             slug='lvl_1b',
                                             text='text')

        lvl_2a = SummaryText.add_summarytext(assessment=self.assessment_working,
                                             parent=[lvl_1a],
                                             title='lvl_2a',
                                             slug='lvl_2a',
                                             text='text')

        lvl_2b = SummaryText.add_summarytext(assessment=self.assessment_working,
                                             sibling=[lvl_2a],
                                             title='lvl_2b',
                                             slug='lvl_2b',
                                             text='text')

        assessment_root = SummaryText.get_assessment_root_node(self.assessment_working)

        tree_form = SummaryText.dump_bulk(assessment_root)
        # print pprint.pprint(tree_form)

        SummaryTextTests.clean_json(tree_form)
        self.assertEqual(json.dumps(tree_form),"""[{"data": {"title": "assessment-1"}, "children": [{"data": {"title": "lvl_1a"}, "children": [{"data": {"title": "lvl_2a"}}, {"data": {"title": "lvl_2b"}}]}, {"data": {"title": "lvl_1b"}}]}]""")


        # Swap 2a and 2b
        lvl_2b.move_summarytext(parent=lvl_1a, sibling=None)
        tree_form = SummaryText.dump_bulk(assessment_root)
        SummaryTextTests.clean_json(tree_form)
        self.assertEqual(json.dumps(tree_form),"""[{"data": {"title": "assessment-1"}, "children": [{"data": {"title": "lvl_1a"}, "children": [{"data": {"title": "lvl_2b"}}, {"data": {"title": "lvl_2a"}}]}, {"data": {"title": "lvl_1b"}}]}]""")

        # Swap back
        lvl_2b.move_summarytext(parent=None, sibling=lvl_2a)
        tree_form = SummaryText.dump_bulk(assessment_root)
        SummaryTextTests.clean_json(tree_form)
        self.assertEqual(json.dumps(tree_form),"""[{"data": {"title": "assessment-1"}, "children": [{"data": {"title": "lvl_1a"}, "children": [{"data": {"title": "lvl_2a"}}, {"data": {"title": "lvl_2b"}}]}, {"data": {"title": "lvl_1b"}}]}]""")

