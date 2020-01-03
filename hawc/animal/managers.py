from django.apps import apps
from utils.models import BaseManager, get_distinct_charfield_opts, \
    get_distinct_charfield


class ExperimentManager(BaseManager):
    assessment_relation = 'study__assessment'


class AnimalGroupManager(BaseManager):
    assessment_relation = 'experiment__study__assessment'


class DosingRegimeManager(BaseManager):
    assessment_relation = 'dosed_animals__experiment__study__assessment'


class DoseGroupManager(BaseManager):
    assessment_relation = 'dose_regime__dosed_animals__experiment__study__assessment'

    def by_dose_regime(self, dose_regime):
        return self.filter(dose_regime=dose_regime)

class EndpointManager(BaseManager):
    assessment_relation = 'assessment'

    def published(self, assessment_id=None):
        return self.get_qs(assessment_id)\
                    .filter(animal_group__experiment__study__published=True)

    def tag_qs(self, assessment_id, tag_slug=None):
        AnimalGroup = apps.get_model('animal', 'AnimalGroup')
        Experiment = apps.get_model('animal', 'Experiment')
        Study = apps.get_model('study', 'Study')
        return self.filter(effects__slug=tag_slug)\
                    .select_related(
                        'animal_group',
                        'animal_group__dosing_regime'
                    ).prefetch_related(
                        'animal_group__dosing_regime__doses'
                    ).filter(
                        animal_group__in=AnimalGroup.objects.filter(
                            experiment__in=Experiment.objects.filter(
                                study__in=Study.objects.get_qs(
                                    assessment_id
                    ))))

    def optimized_qs(self, **filters):
        return self.filter(**filters)\
                    .select_related(
                        'animal_group',
                        'animal_group__dosed_animals',
                        'animal_group__experiment',
                        'animal_group__experiment__study',
                    ).prefetch_related(
                        'groups',
                        'effects',
                        'animal_group__dosed_animals__doses',
                    )

    def get_system_choices(self, assessment_id):
        return get_distinct_charfield_opts(self, assessment_id, 'system')

    def get_organ_choices(self, assessment_id):
        return get_distinct_charfield_opts(self, assessment_id, 'organ')

    def get_effect_choices(self, assessment_id):
        return get_distinct_charfield_opts(self, assessment_id, 'effect')

    def get_effect_subtype_choices(self, assessment_id):
        return get_distinct_charfield_opts(self, assessment_id, 'effect_subtype')

    def get_effects(self, assessment_id):
        return get_distinct_charfield(self, assessment_id, 'effect')


class EndpointGroupManager(BaseManager):
    assessment_relation = 'endpoint__assessment'
