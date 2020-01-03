from django.core.management import call_command

from myuser.models import HAWCUser
from assessment import models


def build_dose_units_for_permission_testing(obj):
    obj.dose_units = models.DoseUnits.objects.create(name='mg/kg/day')


def build_species_for_permission_testing(obj):
    obj.species = models.Species.objects.create(name='orangutan')


def build_strain_for_permission_testing(obj):
    obj.strain = models.Strain.objects.create(
        name='sumatran',
        species=obj.species)


def build_assessments_for_permissions_testing(obj):
    # builds assessments to be used for tests; note that other test-suites may
    # call this function as well

    try:
        call_command('createcachetable', 'dev_cache_table', interactive=False)
    except:
        pass

    obj.superuser = HAWCUser.objects.create_superuser('sudo@sudo.com', 'pw')
    obj.project_manager = HAWCUser.objects.create_user('pm@pm.com', 'pw')
    obj.team_member = HAWCUser.objects.create_user('team@team.com', 'pw')
    obj.reviewer = HAWCUser.objects.create_user('rev@rev.com', 'pw')

    # setup working assessment
    obj.assessment_working = models.Assessment.objects.create(
        name='working',
        year=1999,
        version='1.0',
        editable=True,
        public=False
    )

    obj.assessment_working.project_manager.add(obj.project_manager)
    obj.assessment_working.team_members.add(obj.team_member)
    obj.assessment_working.reviewers.add(obj.reviewer)

    # setup final assessment
    obj.assessment_final = models.Assessment.objects.create(
        name='final',
        year=2001,
        version='final',
        editable=False,
        public=True
    )
    obj.assessment_final.project_manager.add(obj.project_manager)
    obj.assessment_final.team_members.add(obj.team_member)
    obj.assessment_final.reviewers.add(obj.reviewer)

    # additional assessment-level requirements
    build_species_for_permission_testing(obj)
    build_strain_for_permission_testing(obj)
    build_dose_units_for_permission_testing(obj)
