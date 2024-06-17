import pytest
from rest_framework.exceptions import ValidationError

from hawc.apps.common.serializers import (
    FlexibleChoiceArrayField,
    FlexibleChoiceField,
    FlexibleDBLinkedChoiceField,
    check_ids,
    get_matching_instance,
    get_matching_instances,
)
from hawc.apps.epi.models import ResultMetric
from hawc.apps.epi.serializers import ResultMetricSerializer
from hawc.apps.study.models import Study


@pytest.mark.django_db
def test_get_matching_instance(db_keys):
    working = Study.objects.get(id=db_keys.study_working)

    # successes
    for data in [
        {"study_id": db_keys.study_working},
        {"study_id": str(db_keys.study_working)},
    ]:
        assert working == get_matching_instance(Study, data, "study_id")

    # failures
    for data in [
        {},
        {"study_id": -1},
        {"study_id": 999},
        {"study_id": None},
        {"study_id": "string"},
    ]:
        with pytest.raises(ValidationError):
            get_matching_instance(Study, data, "study_id")


@pytest.mark.django_db
def test_get_matching_instances(db_keys):
    working = Study.objects.get(id=db_keys.study_working)

    # successes
    for data in [{"study_id": [db_keys.study_working]}, {"study_id": [str(db_keys.study_working)]}]:
        assert working == get_matching_instances(Study, data, "study_id")[0]

    # failures
    for data in [
        {},
        {"study_id": None},
        {"study_id": [-1]},
        {"study_id": [999]},
        {"study_id": ["string"]},
        {"study_id": "string"},
    ]:
        with pytest.raises(ValidationError):
            get_matching_instances(Study, data, "study_id")


@pytest.mark.django_db
def test_FlexibleChoiceField(db_keys):
    """
    Test the FlexibleChoiceField

    Tests FlexibleChoiceField with keys, display values (case insensitive and not), and bad inputs.
    """
    SAMPLE_NUMERIC_CHOICES = ((0, "example"), (1, "test"))

    SAMPLE_TEXT_CHOICES = (("name", "nom de plume"), ("job", "occupation"))

    numeric_choice = FlexibleChoiceField(choices=SAMPLE_NUMERIC_CHOICES)
    text_choice = FlexibleChoiceField(choices=SAMPLE_TEXT_CHOICES)

    # Either the key or a case insensitive version will resolve to the same internal value
    for valid_input in [1, "test", "TeSt"]:
        assert numeric_choice.to_internal_value(valid_input) == 1

    # Works for text or numeric keys
    for valid_input in ["job", "occupation", "OcCuPaTiOn"]:
        assert text_choice.to_internal_value(valid_input) == "job"

    for invalid_input in [99, "bad input"]:
        with pytest.raises(ValidationError):
            numeric_choice.to_internal_value(invalid_input)

    # Should convert raw values to readable ones
    assert numeric_choice.to_representation(0) == "example"
    assert numeric_choice.to_representation(1) == "test"

    # Should throw KeyError if given a bad value to convert
    with pytest.raises(KeyError):
        numeric_choice.to_representation(2)


@pytest.mark.django_db
def test_FlexibleDBLinkedChoiceField(db_keys):
    """
    Test the FlexibleDBLinkedChoiceField

    Tests FlexibleDBLinkedChoiceField with keys, case-insensitive display values, and bad inputs. Tests in single and "many" mode.
    """
    # This will work with other things besides ResultMetric, it just makes a fine test
    result_metrics = ResultMetric.objects.all()
    result_metrics_list = list(result_metrics)

    # Make sure we have something to test against; test db has 2 metrics in it as of the writing of this test
    assert len(result_metrics_list) >= 2

    first_metric = result_metrics_list[0]
    second_metric = result_metrics_list[1]

    # To be clear - this is multiple tests of single values at a time...
    valid_inputs = []
    valid_inputs.append(first_metric.id)
    valid_inputs.append(first_metric.metric.lower())
    valid_inputs.append(first_metric.metric.upper())

    # ...and this will be a single test of many values at a time
    valid_many_input = [first_metric.id, second_metric.metric.upper()]

    single_demo = FlexibleDBLinkedChoiceField(ResultMetric, ResultMetricSerializer, "metric", False)
    many_demo = FlexibleDBLinkedChoiceField(ResultMetric, ResultMetricSerializer, "metric", True)

    # Test good inputs on the simple "single" case
    for valid_input in valid_inputs:
        looked_up_metric = single_demo.to_internal_value(valid_input)
        assert looked_up_metric.id == first_metric.id

    # Test bad inputs on the simple "single" case
    for invalid_input in [99, "bad input"]:
        with pytest.raises(ValidationError):
            single_demo.to_internal_value(invalid_input)

    # Test good inputs on the "many" case
    looked_up_list = many_demo.to_internal_value(valid_many_input)
    saw_first_metric = False
    saw_second_metric = False
    for looked_up_metric in looked_up_list:
        if looked_up_metric.id == first_metric.id:
            saw_first_metric = True
        elif looked_up_metric.id == second_metric.id:
            saw_second_metric = True
    assert saw_first_metric is True and saw_second_metric is True

    # Test bad input on the "many" case
    for invalid__many_input in [[first_metric.id, second_metric.id * -1], "invalid input", False]:
        with pytest.raises(ValidationError):
            many_demo.to_internal_value(invalid__many_input)

    # Test serialization on the single case
    serialized_metric = single_demo.to_representation(first_metric)
    assert serialized_metric["id"] == first_metric.id
    assert serialized_metric["metric"] == first_metric.metric

    # Test serialization on the many case
    serialized_metrics = many_demo.to_representation(result_metrics)
    assert len(serialized_metrics) == len(result_metrics_list)
    assert serialized_metrics[0]["id"] == first_metric.id
    assert serialized_metrics[1]["id"] == second_metric.id


class TestFlexibleChoiceArrayField:
    SAMPLE_NUMERIC_CHOICES = ((0, "example"), (1, "test"))
    SAMPLE_TEXT_CHOICES = (("name", "nom de plume"), ("job", "occupation"))

    def test_to_internal_value(self):
        numeric_choice = FlexibleChoiceArrayField(choices=self.SAMPLE_NUMERIC_CHOICES)
        text_choice = FlexibleChoiceArrayField(choices=self.SAMPLE_TEXT_CHOICES)

        # Either the key or a case insensitive version will resolve to the same internal value
        for valid_input in (["test", 0], ["tEsT", "EXAMPLE"], [1, "example"]):
            converted = numeric_choice.to_internal_value(valid_input)
            assert len(converted) == 2 and converted[0] == 1 and converted[1] == 0

        # Works for text or numeric keys
        for valid_input in (["job", "occupation", "OcCuPaTiOn"],):
            converted = text_choice.to_internal_value(valid_input)
            assert len(set(converted)) == 1 and converted[0] == "job"

        # properly raise validation error for bad data
        for invalid_input in (["example", "bad input"], [1, "another bad input"]):
            with pytest.raises(ValidationError):
                numeric_choice.to_internal_value(invalid_input)

    def test_to_representation(self):
        numeric_choice = FlexibleChoiceArrayField(choices=self.SAMPLE_NUMERIC_CHOICES)
        text_choice = FlexibleChoiceArrayField(choices=self.SAMPLE_TEXT_CHOICES)

        # Should convert raw values to readable ones
        assert numeric_choice.to_representation([0])[0] == "example"
        assert numeric_choice.to_representation([1])[0] == "test"
        assert text_choice.to_representation(["name"])[0] == "nom de plume"

        # Should throw KeyError if given a bad value to convert
        with pytest.raises(KeyError):
            numeric_choice.to_representation([2])


def test_check_ids():
    assert check_ids([]) == []
    assert check_ids([{"id": 1}, {"id": 2}]) == [1, 2]

    for case in [
        "string",
        ["string"],
        {"id": 1},
        [{"name": "bob"}],
        [{"id": "bob"}],
        [{"id": None}],
    ]:
        with pytest.raises(ValidationError):
            check_ids(case)
