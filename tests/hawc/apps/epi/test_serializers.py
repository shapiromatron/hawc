import pytest
from model_bakery import baker

from hawc.apps.epi.serializers import ComparisonSetSerializer


def assert_error(serializer, message):
    assert serializer.is_valid() is False
    assert serializer.errors == {"non_field_errors": [message]}


@pytest.mark.django_db
class TestComparisonSet:
    both_or_neither = "Must supply either a study_population or an outcome, but not both"

    def test_update_cant_set_both_study_population_and_outcome(self):
        study = baker.make("study.Study")
        study_population = baker.make("epi.StudyPopulation", study=study)
        outcome = baker.make("epi.Outcome", study_population=study_population)
        instance = baker.make("epi.ComparisonSet", study_population=study_population)

        serializer = ComparisonSetSerializer(instance, data={"outcome": outcome.id}, partial=True)
        assert_error(serializer, self.both_or_neither)

    def test_create_requires_exactly_one_of_study_population_or_outcome(self):
        serializer = ComparisonSetSerializer(data={"name": "name"})
        assert_error(serializer, self.both_or_neither)

    def test_create_exposure_and_study_population_same_study(self):
        study_population = baker.make("epi.StudyPopulation", study=baker.make("study.Study"))
        other = baker.make("epi.StudyPopulation", study=baker.make("study.Study"))
        exposure = baker.make("epi.Exposure", study_population=other)

        data = {"name": "name", "study_population": study_population.id, "exposure": exposure.id}
        assert_error(
            ComparisonSetSerializer(data=data),
            "Supplied exposure and study_population are part of different studies.",
        )

    def test_create_exposure_and_outcome_same_study(self):
        study_population = baker.make("epi.StudyPopulation", study=baker.make("study.Study"))
        outcome = baker.make("epi.Outcome", study_population=study_population)
        other = baker.make("epi.StudyPopulation", study=baker.make("study.Study"))
        exposure = baker.make("epi.Exposure", study_population=other)

        data = {"name": "name", "outcome": outcome.id, "exposure": exposure.id}
        assert_error(
            ComparisonSetSerializer(data=data),
            "Supplied exposure and outcome are part of different studies.",
        )

    def test_update_study_population_same_study(self):
        study_population = baker.make("epi.StudyPopulation", study=baker.make("study.Study"))
        other = baker.make("epi.StudyPopulation", study=baker.make("study.Study"))
        instance = baker.make("epi.ComparisonSet", study_population=study_population)

        serializer = ComparisonSetSerializer(
            instance, data={"study_population": other.id}, partial=True
        )
        assert_error(serializer, "Supplied study_population not study.")

    def test_update_exposure_same_study(self):
        study_population = baker.make("epi.StudyPopulation", study=baker.make("study.Study"))
        other = baker.make("epi.StudyPopulation", study=baker.make("study.Study"))
        exposure = baker.make("epi.Exposure", study_population=other)
        instance = baker.make("epi.ComparisonSet", study_population=study_population)

        serializer = ComparisonSetSerializer(instance, data={"exposure": exposure.id}, partial=True)
        assert_error(serializer, "Supplied exposure not in study.")

    def test_update_outcome_same_study(self):
        study_population = baker.make("epi.StudyPopulation", study=baker.make("study.Study"))
        outcome = baker.make("epi.Outcome", study_population=study_population)
        other = baker.make("epi.StudyPopulation", study=baker.make("study.Study"))
        other_outcome = baker.make("epi.Outcome", study_population=other)
        instance = baker.make("epi.ComparisonSet", outcome=outcome, study_population=None)

        serializer = ComparisonSetSerializer(
            instance, data={"outcome": other_outcome.id}, partial=True
        )
        assert_error(serializer, "Supplied outcome not in study.")
