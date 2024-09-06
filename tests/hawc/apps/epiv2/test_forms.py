from copy import deepcopy

import pytest

from hawc.apps.epiv2 import constants, forms, models


@pytest.mark.django_db
class TestExposureLevelForm:
    def test_clean(self):
        instance = models.ExposureLevel.objects.first()

        form = forms.ExposureLevelForm({}, instance=instance)
        data = {f"exposurelevel-{instance.pk}-{k}": v for k, v in deepcopy(form.initial).items()}

        # test success
        form = forms.ExposureLevelForm(data, instance=instance)
        assert form.is_valid()

        # test `variance_type`
        data2 = deepcopy(data)
        data2.update(
            {
                f"exposurelevel-{instance.pk}-variance_type": constants.VarianceType.NA,
                f"exposurelevel-{instance.pk}-variance": 1,
            }
        )
        form = forms.ExposureLevelForm(data2, instance=instance)
        assert form.is_valid() is False
        assert "variance_type" in form.errors

        data2.update(
            {
                f"exposurelevel-{instance.pk}-variance_type": constants.VarianceType.SD,
                f"exposurelevel-{instance.pk}-variance": 1,
            }
        )
        form = forms.ExposureLevelForm(data2, instance=instance)
        assert form.is_valid() is True

        # test `ci_type`
        data2 = deepcopy(data)
        data2.update(
            {
                f"exposurelevel-{instance.pk}-ci_type": constants.ConfidenceIntervalType.NA,
                f"exposurelevel-{instance.pk}-ci_ucl": 1,
            }
        )
        form = forms.ExposureLevelForm(data2, instance=instance)
        assert form.is_valid() is False
        assert "ci_type" in form.errors

        data2.update(
            {
                f"exposurelevel-{instance.pk}-ci_type": constants.ConfidenceIntervalType.P95,
                f"exposurelevel-{instance.pk}-ci_ucl": 1,
            }
        )
        form = forms.ExposureLevelForm(data2, instance=instance)
        assert form.is_valid() is True


@pytest.mark.django_db
class TestDataExtractionForm:
    def test_clean(self):
        instance = models.DataExtraction.objects.first()

        form = forms.DataExtractionForm({}, instance=instance)
        data = {f"dataextraction-{instance.pk}-{k}": v for k, v in deepcopy(form.initial).items()}

        # test success
        form = forms.DataExtractionForm(data, instance=instance)
        assert form.is_valid()

        # test `variance_type`
        data2 = deepcopy(data)
        data2.update(
            {
                f"dataextraction-{instance.pk}-variance_type": constants.VarianceType.NA,
                f"dataextraction-{instance.pk}-variance": 1,
            }
        )
        form = forms.DataExtractionForm(data2, instance=instance)
        assert form.is_valid() is False
        assert "variance_type" in form.errors

        data2.update(
            {
                f"dataextraction-{instance.pk}-variance_type": constants.VarianceType.SD,
                f"dataextraction-{instance.pk}-variance": 1,
            }
        )
        form = forms.DataExtractionForm(data2, instance=instance)
        assert form.is_valid() is True

        # test `ci_type`
        data2 = deepcopy(data)
        data2.update(
            {
                f"dataextraction-{instance.pk}-ci_type": constants.ConfidenceIntervalType.NA,
                f"dataextraction-{instance.pk}-ci_ucl": 1,
            }
        )
        form = forms.DataExtractionForm(data2, instance=instance)
        assert form.is_valid() is False
        assert "ci_type" in form.errors

        data2.update(
            {
                f"dataextraction-{instance.pk}-ci_type": constants.ConfidenceIntervalType.P95,
                f"dataextraction-{instance.pk}-ci_ucl": 1,
            }
        )
        form = forms.DataExtractionForm(data2, instance=instance)
        assert form.is_valid() is True
