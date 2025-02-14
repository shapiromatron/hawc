import pytest
from django.core.files.base import ContentFile

from hawc.apps.animal.models import EndpointGroup, Experiment
from hawc.apps.assessment.models import Assessment
from hawc.apps.epiv2.models import DataExtraction, Design
from hawc.apps.riskofbias.actions import clone_approach
from hawc.apps.riskofbias.models import RiskOfBiasScore, RiskOfBiasScoreOverrideObject
from hawc.apps.study.actions.clone import (
    CloneStudyDataValidation,
    RobCloneCopyMode,
    clone_animal_bioassay,
    clone_epiv2,
    clone_study,
)
from hawc.apps.study.models import Attachment, Study

from ..test_utils import get_user


@pytest.mark.django_db
class TestDeepClone:
    def test_deep_clone(self, db_keys):
        user = get_user("pm")
        # test study, animal, and epiv2 clone
        src_study = Study.objects.get(id=db_keys.study_working)
        Attachment.objects.create(study=src_study, attachment=ContentFile("test", name="z.txt"))
        assert src_study.attachments.count() == 1
        assert src_study.experiments.count() == 1
        assert src_study.designs.count() == 2

        # create a new destination assessment
        dst_assessment = Assessment.objects.create(name="z", version="y", year=2000)
        dst_assessment.project_manager.set([user])

        # check study clone
        assert Study.objects.filter(assessment=dst_assessment).count() == 0
        clone_map, dst_study = clone_study(src_study, dst_assessment)
        assert Study.objects.filter(assessment=dst_assessment).count() == 1

        # check animal clone
        assert Experiment.objects.filter(study__assessment=dst_assessment).count() == 0
        clone_map = clone_animal_bioassay(src_study, dst_study)
        keys = "experiment animalgroup dosingregime dosegroup endpoint endpointgroup"
        for key in keys.split(" "):
            assert key in clone_map and len(clone_map[key]) > 0
        assert Experiment.objects.filter(study__assessment=dst_assessment).count() == 1

        # check epiv2 clone
        assert Design.objects.filter(study__assessment=dst_assessment).count() == 0
        clone_map = clone_epiv2(src_study, dst_study)
        for key in [
            "design",
            "chemical",
            "exposure",
            "exposurelevel",
            "outcome",
            "adjustmentfactor",
            "dataextraction",
        ]:
            assert key in clone_map and len(clone_map[key]) > 0
        assert Design.objects.filter(study__assessment=dst_assessment).count() == 2

        # delete our new assessment, which deletes all our clones
        dst_assessment.delete()

        # confirm we have all the data on our src assessment
        assert src_study.attachments.count() == 1
        assert src_study.experiments.count() == 1
        assert src_study.designs.count() == 2
        assert EndpointGroup.objects.filter(
            endpoint__animal_group__experiment__study=src_study
        ).exists()
        assert DataExtraction.objects.filter(design__study=src_study).exists()
        return

    def test_deep_clone_study_evaluation(self, db_keys):
        user = get_user("pm")
        # test study evaluation
        src_study_id = 7
        src_study = Study.objects.get(id=src_study_id)

        assert src_study.riskofbiases.filter(active=True, final=True).exists()
        qs = RiskOfBiasScore.objects.filter(is_default=False, riskofbias__study=src_study)
        assert qs.exists()
        qs = RiskOfBiasScoreOverrideObject.objects.filter(score__riskofbias__study=src_study)
        assert qs.exists()

        # create a new destination assessment
        dst_assessment = Assessment.objects.create(name="z", version="y", year=2000)
        dst_assessment.project_manager.set([user])
        metric_map = clone_approach(dst_assessment, src_study.assessment, user_id=user.id)
        clone_request = CloneStudyDataValidation(
            study={src_study_id},
            study_bioassay={src_study_id},
            study_rob={src_study_id},
            study_epi=set(),
            include_rob=True,
            copy_mode=RobCloneCopyMode.final_to_final,
            metric_map=metric_map,
        )
        study_map = clone_request.clone(
            user,
            {"assessment": dst_assessment, "studies": Study.objects.filter(id=src_study_id)},
        )

        dst_study, dst_mapping = study_map[src_study]
        assert isinstance(dst_study, Study)
        for key in ["riskofbias", "riskofbiasscore", "riskofbiasscoreoverrideobject"]:
            assert key in dst_mapping["riskofbias"] and len(dst_mapping["riskofbias"][key]) > 0

        # delete our new assessment, which deletes all our clones
        dst_assessment.delete()

        # confirm we have all the data on our src assessment
        assert src_study.riskofbiases.filter(active=True, final=True).exists()
        qs = RiskOfBiasScore.objects.filter(is_default=False, riskofbias__study=src_study)
        assert qs.exists()
        qs = RiskOfBiasScoreOverrideObject.objects.filter(score__riskofbias__study=src_study)
        assert qs.exists()
