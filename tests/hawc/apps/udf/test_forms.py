import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.common.forms import BaseFormHelper
from hawc.apps.udf import forms, models

from ..test_utils import get_user


@pytest.mark.django_db
class TestUDFForm:
    def test_init(self, db_keys):
        user = get_user("pm")
        form = forms.UDFForm(user=user)
        assert form.instance.creator == user

    def test_clean_name(self, db_keys):
        user = get_user("pm")

        # Create a UDF first
        models.UserDefinedForm.objects.create(
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

        # Test a valid dataset passes check
        data.update(name="Test UDF 2")
        form = forms.UDFForm(data, user=user)
        assert form.is_valid() is True

    def test_helper(self, db_keys):
        user = get_user("pm")
        form = forms.UDFForm(user=user)
        helper = form.helper
        assert isinstance(helper, BaseFormHelper)


@pytest.mark.django_db
class TestModelBindingForm:
    def test_init(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        user = get_user("pm")
        form = forms.ModelBindingForm(parent=assessment, user=user)
        assert form.instance.assessment == assessment
        assert form.instance.creator == user
        assert form.fields["assessment"].initial == assessment

    def test_helper(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        user = get_user("pm")
        form = forms.ModelBindingForm(parent=assessment, user=user)
        helper = form.helper
        assert isinstance(helper, BaseFormHelper)


@pytest.mark.django_db
class TestTagBindingForm:
    def test_init(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        user = get_user("pm")
        form = forms.TagBindingForm(parent=assessment, user=user)
        assert form.instance.assessment == assessment
        assert form.instance.creator == user
        assert form.fields["assessment"].initial == assessment

    def test_helper(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        user = get_user("pm")
        form = forms.TagBindingForm(parent=assessment, user=user)
        helper = form.helper
        assert isinstance(helper, BaseFormHelper)
