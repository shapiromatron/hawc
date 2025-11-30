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

    def test_helper(self):
        instance = models.ExposureLevel.objects.first()
        form = forms.ExposureLevelForm(instance=instance)
        helper = form.helper
        assert helper is not None


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

    def test_helper(self):
        instance = models.DataExtraction.objects.first()
        form = forms.DataExtractionForm(instance=instance)
        helper = form.helper
        assert helper is not None


@pytest.mark.django_db
class TestExposureForm:
    def test_init(self, db_keys):
        design = models.Design.objects.get(id=db_keys.epiv2_design)
        form = forms.ExposureForm(parent=design)
        assert form.fields["measurement_type"].widget.attrs["data-name"] == "measurement_type"
        assert (
            form.fields["biomonitoring_matrix"].widget.attrs["data-name"] == "biomonitoring_matrix"
        )

    def test_helper(self, db_keys):
        design = models.Design.objects.get(id=db_keys.epiv2_design)
        form = forms.ExposureForm(parent=design)
        helper = form.helper
        assert helper is not None


@pytest.mark.django_db
class TestAdjustmentFactorForm:
    def test_helper(self, db_keys):
        design = models.Design.objects.get(id=db_keys.epiv2_design)
        form = forms.AdjustmentFactorForm(parent=design)
        helper = form.helper
        assert helper is not None


@pytest.mark.django_db
class TestOutcomeForm:
    def test_helper(self, db_keys):
        design = models.Design.objects.get(id=db_keys.epiv2_design)
        form = forms.OutcomeForm(parent=design)
        helper = form.helper
        assert helper is not None
