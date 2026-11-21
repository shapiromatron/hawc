import pytest

from hawc.apps.summary.constants import StudyType, VisualType, get_default_evidence_type


class TestStudyType:
    @pytest.mark.parametrize(
        ("study_type", "filter_prefix"),
        [
            (StudyType.BIOASSAY, "bioassay"),
            (StudyType.EPI, "epi"),
            (StudyType.EPI_META, "epi_meta"),
            (StudyType.IN_VITRO, "in_vitro"),
            (StudyType.ECO, "eco"),
        ],
    )
    def test_study_filter_prefix(self, study_type, filter_prefix):
        assert study_type.study_filter_prefix() == filter_prefix

    @pytest.mark.parametrize(
        ("study_type", "rob_prefix"),
        [
            (StudyType.BIOASSAY, "required_animal"),
            (StudyType.EPI, "required_epi"),
            (StudyType.EPI_META, None),
            (StudyType.IN_VITRO, "required_invitro"),
            (StudyType.ECO, None),
        ],
    )
    def test_rob_prefix(self, study_type, rob_prefix):
        if rob_prefix is None:
            with pytest.raises(KeyError):
                study_type.rob_prefix()
        else:
            assert study_type.rob_prefix() == rob_prefix


def test_default_evidence_type():
    assert get_default_evidence_type(VisualType.BIOASSAY_AGGREGATION) == StudyType.BIOASSAY
    assert get_default_evidence_type(VisualType.DATA_PIVOT_FILE) == StudyType.OTHER
    with pytest.raises(ValueError, match="multiple exist"):
        get_default_evidence_type(VisualType.DATA_PIVOT_QUERY)
