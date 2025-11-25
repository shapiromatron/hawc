import pytest

from hawc.apps.eco import forms, models


@pytest.mark.django_db
class TestCauseForm:
    def test_helper_property(self, db_keys):
        # Test helper property
        design = models.Design.objects.get(id=db_keys.eco_design)
        form = forms.CauseForm(parent=design)
        helper = form.helper
        assert helper is not None


@pytest.mark.django_db
class TestEffectForm:
    def test_helper_property(self, db_keys):
        # Test helper property
        design = models.Design.objects.get(id=db_keys.eco_design)
        form = forms.EffectForm(parent=design)
        helper = form.helper
        assert helper is not None


@pytest.mark.django_db
class TestResultForm:
    def test_helper_property(self, db_keys):
        # Test helper property
        design = models.Design.objects.get(id=db_keys.eco_design)
        form = forms.ResultForm(parent=design)
        helper = form.helper
        assert helper is not None

    def test_clean_validation(self, db_keys):
        # Test clean method validation
        design = models.Design.objects.get(id=db_keys.eco_design)
        result = models.Result.objects.filter(design=design).first()
        
        if result:
            # Get initial data from the existing result
            form = forms.ResultForm(instance=result)
            initial_data = {f"result-{result.pk}-{k}": v for k, v in form.initial.items()}
            
            # Test with lower variability but no variability value
            data = initial_data.copy()
            data[f"result-{result.pk}-low_variability"] = 1.0
            data[f"result-{result.pk}-variability"] = None
            
            form = forms.ResultForm(data, instance=result)
            assert form.is_valid() is False
            assert "variability" in form.errors
            assert forms.ResultForm.RESPONSE_VARIABILITY_REQ in form.errors["variability"]

