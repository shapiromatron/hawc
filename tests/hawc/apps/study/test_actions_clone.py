import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from hawc.apps.animal.models import Experiment
from hawc.apps.epiv2.models import Design
from hawc.apps.riskofbias.actions import clone_approach
from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasMetric, RiskOfBiasScoreOverrideObject
from hawc.apps.study.actions.clone import clone_animal_bioassay, clone_epiv2, clone_rob, clone_study
from hawc.apps.study.models import Study

from ..test_utils import get_client


@pytest.mark.django_db
class TestDeepClone:
    def test_deep_clone(self, db_keys):
        src_study = db_keys.study_working
        dst_assessment = db_keys.assessment_conflict_resolution

        # add attachment
        client = get_client("pm", htmx=True)
        url = reverse("study:attachment_create", args=[src_study])
        resp = client.post(
            url,
            {"attachment": SimpleUploadedFile("zzzz.txt", b"test")},
            follow=True,
        )
        assert resp.status_code == 200

        clone_map = clone_study(src_study, dst_assessment)
        dst_study = clone_map["study"][src_study]
        assert len(Study.objects.filter(assessment=dst_assessment)) == 2

        clone_map = {
            **clone_map,
            **clone_animal_bioassay(src_study, dst_study),
            **clone_epiv2(src_study, dst_study),
        }
        assert len(Experiment.objects.filter(study_id=dst_study)) == 1
        assert len(Design.objects.filter(study_id=dst_study)) == 2

        clone_approach(
            Study.objects.get(pk=dst_study).assessment,
            Study.objects.get(pk=src_study).assessment,
        )
        src_metrics = RiskOfBiasMetric.objects.filter(
            domain__assessment=Study.objects.get(pk=src_study).assessment
        )
        dst_metrics = RiskOfBiasMetric.objects.filter(
            domain__assessment=Study.objects.get(pk=dst_study).assessment
        )
        metric_map = {str(src.id): dst_metrics[i].id for i, src in enumerate(src_metrics)}

        clone_rob(src_study, dst_study, metric_map, clone_map)
        assert len(RiskOfBias.objects.filter(study_id=dst_study)) == 3
        assert (
            len(RiskOfBiasScoreOverrideObject.objects.filter(score__riskofbias__study_id=dst_study))
            == 1
        )
