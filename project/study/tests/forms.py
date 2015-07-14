import re

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from .utils import build_studies_for_permission_testing


class StudyFormTests(TestCase):
    """
    Test cases for internal form logic.
    """
    def setUp(self):
        build_studies_for_permission_testing(self)

    def test_uf_value(self):
        c = Client()
        self.assertTrue(c.login(username='team@team.com', password='pw'))

        new_study_url = reverse('study:new_ref', kwargs={'pk': self.assessment_working.pk})
        study_dict = {
            'short_citation': 'foo et al.',
            'full_citation': 'cite',
            'study_type': 0,
            'coi_reported': 0
        }

        # can create a new study field
        response = c.post(new_study_url, study_dict)
        pk = re.findall(r'/study/(\d+)/$', response['location'])
        pk = int(pk[0])
        self.assertRedirects(response, reverse('study:detail', kwargs={'pk': pk}))

        # can't create a new study citation field that already exists
        response = c.post(new_study_url, study_dict)
        self.assertFormError(response, 'form', None, u'Error- short-citation name must be unique for assessment.')

        # can change an existing study citation field to a different type
        response = c.post(reverse('study:update', kwargs={'pk': pk}), study_dict)
        self.assertTrue(response.status_code in [200, 302])
        self.assertTemplateUsed('study/study_detail.html')

        # can create a new study in different assessment
        c.logout()
        self.assertTrue(c.login(username='sudo@sudo.com', password='pw'))

        response = c.post(
            reverse('study:new_ref', kwargs={'pk': self.assessment_final.pk}),
            study_dict)
        pk = re.findall(r'/study/(\d+)/$', response['location'])
        pk = int(pk[0])
        self.assertRedirects(response, reverse('study:detail', kwargs={'pk': pk}))
