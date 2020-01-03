from study.models import Study
from assessment.tests.utils import build_assessments_for_permissions_testing


def build_studies_for_permission_testing(obj):
    build_assessments_for_permissions_testing(obj)

    obj.study_working = Study.objects.create(
        assessment=obj.assessment_working,
        bioassay=True,
        full_citation="Foo et al.",
        short_citation="Foo et al.")

    obj.study_final = Study.objects.create(
        assessment=obj.assessment_final,
        bioassay=True,
        full_citation="Foo et al.",
        short_citation="Foo et al.")
