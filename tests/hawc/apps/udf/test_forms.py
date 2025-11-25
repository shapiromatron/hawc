import pytest
from django.contrib.contenttypes.models import ContentType

from hawc.apps.assessment.models import Assessment
from hawc.apps.lit.models import ReferenceFilterTag
from hawc.apps.udf import forms, models

from ..test_utils import get_user


@pytest.mark.django_db
class TestUDFForm:
    def test_init_with_creator(self, db_keys):
        # Test initialization with creator
        user = get_user("pm")
        form = forms.UDFForm(user=user)
        assert form.instance.creator == user

    def test_clean_name_validation(self, db_keys):
        # Test clean_name validation
        user = get_user("pm")
        
        # Create a UDF first
        udf1 = models.UserDefinedForm.objects.create(
            creator=user,
            name="Test UDF",
            description="Test",
            schema={"fields": []},
        )
        
        # Try to create another UDF with the same name
        data = {
            "name": "Test UDF",
            "description": "Test",
            "schema": {"fields": []},
            "published": False,
            "deprecated": False,
        }
        form = forms.UDFForm(data, user=user)
        assert form.is_valid() is False
        assert "name" in form.errors
        assert "unique" in form.errors["name"][0].lower()

    def test_helper_property(self, db_keys):
        # Test helper property
        user = get_user("pm")
        form = forms.UDFForm(user=user)
        helper = form.helper
        assert helper is not None


@pytest.mark.django_db
class TestModelBindingForm:
    def test_init_with_parent_and_user(self, db_keys):
        # Test initialization with parent and user
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        user = get_user("pm")
        form = forms.ModelBindingForm(parent=assessment, user=user)
        assert form.instance.assessment == assessment
        assert form.instance.creator == user
        assert form.fields["assessment"].initial == assessment

    def test_helper_property(self, db_keys):
        # Test helper property
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        user = get_user("pm")
        form = forms.ModelBindingForm(parent=assessment, user=user)
        helper = form.helper
        assert helper is not None


@pytest.mark.django_db
class TestTagBindingForm:
    def test_init_with_parent_and_user(self, db_keys):
        # Test initialization with parent and user
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        user = get_user("pm")
        form = forms.TagBindingForm(parent=assessment, user=user)
        assert form.instance.assessment == assessment
        assert form.instance.creator == user
        assert form.fields["assessment"].initial == assessment

    def test_helper_property(self, db_keys):
        # Test helper property
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        user = get_user("pm")
        form = forms.TagBindingForm(parent=assessment, user=user)
        helper = form.helper
        assert helper is not None


@pytest.mark.django_db
class TestUDFModelFormMixin:
    def test_save_method(self, db_keys):
        # Test save method for UDFModelFormMixin
        # This is tested indirectly through forms that use it
        # For now, just verify the mixin exists
        from hawc.apps.study.forms import BaseStudyForm
        from hawc.apps.study.models import Study
        
        study = Study.objects.get(id=db_keys.study_working)
        # Verify that the form has the mixin
        assert hasattr(BaseStudyForm, 'set_udf_field')
