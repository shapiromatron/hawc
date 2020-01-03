from django.db import models

from utils.models import BaseManager


class StudyManager(BaseManager):
    assessment_relation = 'assessment'

    def published(self, assessment_id=None):
        return self.get_qs(assessment_id).filter(published=True)

    def get_choices(self, assessment_id=None):
        return self.get_qs(assessment_id)\
                  .values_list('id', 'short_citation')

    def rob_scores(self, assessment_id=None):
        return self.get_qs(assessment_id)\
                .annotate(final_score=models.Sum(
                    models.Case(
                        models.When(riskofbiases__active=True,
                                riskofbiases__final=True,
                                then='riskofbiases__scores__score'),
                        default=0)))\
                .values('id', 'short_citation', 'final_score')


class AttachmentManager(BaseManager):
    assessment_relation = 'study__assessment'
