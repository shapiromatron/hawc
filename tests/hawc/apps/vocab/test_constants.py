"""Tests for vocab constants - separate from model-specific tests."""

import pytest
from django.contrib import admin
from django.test import RequestFactory
from django.urls import reverse

from hawc.apps.vocab.admin import TermAdmin
from hawc.apps.vocab.constants import VocabularyNamespace, VocabularyTermType


@pytest.mark.django_db
def test_namespace_properties():
    """Test vocabulary namespace properties."""
    assert VocabularyNamespace.display_choices()
    assert VocabularyNamespace.EHV.display_name.startswith("EPA")
    assert VocabularyNamespace.ToxRefDB.display_name.startswith("EPA")
    assert VocabularyNamespace.EHV.display_url == reverse("vocab:ehv-browse")
    assert VocabularyNamespace.ToxRefDB.display_url == reverse("vocab:toxrefdb-browse")


@pytest.mark.django_db
def test_constants_mappings_and_admin_queryset():
    """Test that constant mappings are correct and admin queryset returns non-zero count."""
    # Verify constant mappings
    assert VocabularyTermType.value_to_text_field()[5] == "name"
    assert VocabularyTermType.value_to_term_field()[5] == "name_term_id"

    # Test admin queryset returns non-zero count (admin is not model-specific)
    # Import Term here since it's needed for the admin test
    from hawc.apps.vocab.models import Term

    admin_obj = TermAdmin(Term, admin.site)
    request = RequestFactory().get("/admin/vocab/term/")
    assert admin_obj.get_queryset(request).count() >= 1
    assert admin_obj.has_delete_permission(request) is False
