import re

import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects, assertTemplateUsed

from hawc.apps.assessment.models import Assessment
from hawc.apps.common.forms import ASSESSMENT_UNIQUE_MESSAGE
from hawc.apps.lit.constants import ReferenceDatabase
from hawc.apps.lit.models import Reference
from hawc.apps.study import forms, models


@pytest.mark.django_db
def test_study_forms(db_keys):
    c = Client()
    assert c.login(username="team@hawcproject.org", password="pw") is True

    new_study_url = reverse("study:new_ref", kwargs={"pk": db_keys.assessment_working})
    study_dict = {
        "short_citation": "foo et al.",
        "full_citation": "cite",
        "bioassay": True,
        "coi_reported": 0,
    }

    # can create a new study field
    response = c.post(new_study_url, study_dict)
    pk = re.findall(r"/study/(\d+)/$", response["location"])
    pk = int(pk[0])
    assertRedirects(response, reverse("study:detail", args=(pk,)))

    # can't create a new study citation field that already exists
    response = c.post(new_study_url, study_dict)
    assertFormError(response.context["form"], "short_citation", ASSESSMENT_UNIQUE_MESSAGE)

    # can change an existing study citation field to a different type
    with assertTemplateUsed("study/study_detail.html"):
        response = c.post(reverse("study:update", args=(pk,)), study_dict, follow=True)
        assert response.status_code == 200

    # can create a new study in different assessment
    c.logout()
    assert c.login(username="admin@hawcproject.org", password="pw") is True

    response = c.post(
        reverse("study:new_ref", kwargs={"pk": db_keys.assessment_final}),
        study_dict,
    )
    pk = re.findall(r"/study/(\d+)/$", response["location"])
    pk = int(pk[0])
    assertRedirects(response, reverse("study:detail", args=(pk,)))


@pytest.mark.django_db
class TestBaseStudyForm:
    def test_init_with_assessment_parent(self, db_keys):
        # Test initialization with Assessment as parent
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        form = forms.BaseStudyForm(parent=assessment)
        assert form.instance.assessment == assessment

    def test_init_with_reference_parent(self, db_keys):
        # Test initialization with Reference as parent
        reference = Reference.objects.get(id=db_keys.reference_linked)
        form = forms.BaseStudyForm(parent=reference)
        assert form.instance.assessment == reference.assessment
        assert form.instance.reference_ptr == reference

    def test_save_with_internal_communications(self, db_keys):
        # Test saving with internal communications
        study = models.Study.objects.get(id=db_keys.study_working)
        data = {
            "short_citation": "Test et al.",
            "full_citation": "Test citation",
            "bioassay": True,
            "coi_reported": 0,
            "internal_communications": "Test communications",
        }
        form = forms.StudyForm(data, instance=study)
        assert form.is_valid()
        saved_study = form.save()
        assert saved_study.get_communications() == "Test communications"


@pytest.mark.django_db
class TestIdentifierStudyForm:
    def test_clean_validation_errors(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)

        # Test with missing db_type
        form = forms.IdentifierStudyForm(
            {"db_id": "12345"}, instance=None, parent=assessment
        )
        assert form.is_valid() is False

        # Test with missing db_id
        form = forms.IdentifierStudyForm(
            {"db_type": str(ReferenceDatabase.PUBMED.value)}, instance=None, parent=assessment
        )
        assert form.is_valid() is False

    def test_clean_existing_study(self, db_keys):
        # Test validation when study with identifier already exists
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        # Get an existing study with an identifier
        study_with_id = models.Study.objects.filter(identifiers__isnull=False).first()
        if study_with_id:
            identifier = study_with_id.identifiers.first()
            form = forms.IdentifierStudyForm(
                {
                    "db_type": str(identifier.database),
                    "db_id": identifier.unique_id,
                },
                instance=None,
                parent=study_with_id.assessment,
            )
            assert form.is_valid() is False
            assert "db_id" in form.errors


@pytest.mark.django_db
class TestAttachmentForm:
    def test_init_with_parent(self, db_keys):
        # Test initialization with study as parent
        study = models.Study.objects.get(id=db_keys.study_working)
        form = forms.AttachmentForm(parent=study)
        assert form.instance.study == study

    def test_helper_property(self, db_keys):
        # Test helper property
        study = models.Study.objects.get(id=db_keys.study_working)
        form = forms.AttachmentForm(parent=study)
        helper = form.helper
        assert helper is not None


@pytest.mark.django_db
class TestNewStudyFromReferenceForm:
    def test_set_helper(self, db_keys):
        # Test setHelper method
        reference = Reference.objects.get(id=db_keys.reference_linked)
        form = forms.NewStudyFromReferenceForm(parent=reference)
        helper = form.helper
        assert helper is not None
