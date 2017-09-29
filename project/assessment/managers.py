import json

from django.apps import apps
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from utils.helper import HAWCDjangoJSONEncoder
from utils.models import BaseManager


class AssessmentManager(BaseManager):
    assessment_relation = 'id'

    def get_public_assessments(self):
        return self.filter(public=True, hide_from_public_page=False)\
                    .order_by('name')

    def get_viewable_assessments(self, user, exclusion_id=None, public=False):
        """
        Return queryset of all assessments which that user is able to view,
        optionally excluding assessment exclusion_id,
        not including public assessments
        """
        filters = (Q(project_manager=user) | Q(team_members=user) | Q(reviewers=user))
        if public:
            filters |= (Q(public=True) & Q(hide_from_public_page=False))
        return self.filter(filters)\
            .exclude(id=exclusion_id)\
            .distinct()

    def get_editable_assessments(self, user, exclusion_id=None):
        """
        Return queryset of all assessments which that user is able to edit,
        optionally excluding assessment exclusion_id,
        not including public assessments
        """
        return self.filter(Q(project_manager=user) | Q(team_members=user))\
            .exclude(id=exclusion_id)\
            .distinct()


class AttachmentManager(BaseManager):

    def get_attachments(self, obj, isPublic):
        filters = {
            "content_type": ContentType.objects.get_for_model(obj),
            "object_id": obj.id
        }
        if isPublic:
            filters["publicly_available"] = True
        return self.filter(**filters)

    def assessment_qs(self, assessment_id):
        a = ContentType.objects\
            .get(app_label="assessment", model="assessment").id
        return self.filter(content_type=a, object_id=assessment_id)


class DoseUnitManager(BaseManager):

    def assessment_qs(self, assessment_id):
        return self.all()

    def json_all(self):
        return json.dumps(list(self.all().values()), cls=HAWCDjangoJSONEncoder)

    def get_animal_units(self, assessment):
        """
        Returns a list of the dose-units which are used in the selected
        assessment for animal bioassay data.
        """
        Study = apps.get_model('study', 'Study')
        Experiment = apps.get_model('animal', 'Experiment')
        AnimalGroup = apps.get_model('animal', 'AnimalGroup')
        DosingRegime = apps.get_model('animal', 'DosingRegime')
        DoseGroup = apps.get_model('animal', 'DoseGroup')
        return self.filter(
            dosegroup__in=DoseGroup.objects.filter(
                dose_regime__in=DosingRegime.objects.filter(
                    dosed_animals__in=AnimalGroup.objects.filter(
                        experiment__in=Experiment.objects.filter(
                            study__in=Study.objects.get_qs(assessment))))))\
            .values_list('name', flat=True)\
            .distinct()


class SpeciesManager(BaseManager):

    def assessment_qs(self, assessment_id):
        return self.all()


class StrainManager(BaseManager):

    def assessment_qs(self, assessment_id):
        return self.all()


class EffectTagManager(BaseManager):
    assessment_relation = 'baseendpoint__assessment'

    def assessment_qs(self, assessment_id):
        return self.filter(baseendpoint__assessment_id=assessment_id)\
            .distinct()

    def get_choices(self, assessment_id):
        return self.get_qs(assessment_id)\
                .values_list('id', 'name')\
                .order_by('name')


class BaseEndpointManager(BaseManager):
    assessment_relation = 'assessment'


class TimeSpentEditingManager(BaseManager):
    assessment_relation = 'assessment'
