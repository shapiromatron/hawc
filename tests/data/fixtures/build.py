from hawc.apps.assessment.models import Assessment
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.study.models import Study
from hawc.apps.animal.models import Experiment
from hawc.apps.epi.models import StudyPopulation


# builds assessments to be used for tests; note that other test-suites may
# call this function as well
superuser = HAWCUser.objects.create_superuser("sudo@sudo.com", "pw")
project_manager = HAWCUser.objects.create_user("pm@pm.com", "pw")
team_member = HAWCUser.objects.create_user("team@team.com", "pw")
reviewer = HAWCUser.objects.create_user("rev@rev.com", "pw")
public = HAWCUser.objects.create_user("public@rev.com", "pw")

# setup working assessment
assessment_working = Assessment.objects.create(
    name="working", year=1999, version="1.0", editable=True, public=False
)

assessment_working.project_manager.add(project_manager)
assessment_working.team_members.add(team_member)
assessment_working.reviewers.add(reviewer)

# setup final assessment
assessment_final = Assessment.objects.create(
    name="final", year=2001, version="final", editable=False, public=True
)
assessment_final.project_manager.add(project_manager)
assessment_final.team_members.add(team_member)
assessment_final.reviewers.add(reviewer)

assessment_data = dict(
    users=dict(
        superuser=superuser,
        project_manager=project_manager,
        team_member=team_member,
        reviewer=reviewer,
        public=public,
    ),
    assessment=dict(assessment_working=assessment_working, assessment_final=assessment_final),
)

study_working = Study.objects.create(
    assessment=assessment_data["assessment"]["assessment_working"],
    bioassay=True,
    full_citation="Foo et al.",
    short_citation="Foo et al.",
)

study_final = Study.objects.create(
    assessment=assessment_data["assessment"]["assessment_final"],
    bioassay=True,
    full_citation="Foo et al.",
    short_citation="Foo et al.",
)
assessment_data["study"] = dict(study_working=study_working, study_final=study_final,)

# exp1 = Experiment.objects.create(study_id=study_working.id, name="experiment-1", type="Ac")
# assessment_data["experiment"] = dict(exp1=exp1)


# sp1 = StudyPopulation.objects.create(study_id=1, name="experiment-1", design="Ac")
# assessment_data["experiment"] = dict(study_id=study_working.id, name="sp-1", design="Co")
# assessment_data["experiment"] = dict(sp1=sp1)
