from datetime import timedelta
import pytest
from django.utils import timezone

# Simple bakery-style helper for creating test data
def bake(model, **kwargs):
    """Create and save a model instance."""
    obj = model(**kwargs)
    obj.save()
    return obj


@pytest.mark.django_db
class TestTermManager:
    """Comprehensive tests for Term manager methods using manual test data creation."""

    def _setup_assessment_data(self):
        """Set up assessment data for manager tests."""
        from hawc.apps.animal.models import Study
        
        # Create or get a study
        study = bake(
            Study,
            name="Test Study Assessment",
        )

        # Create a reference for the study
        reference = bake(
            'animal.Reference',
            id=200,
            title="Test Reference Title",
            doi="10.5678/test-ref",
            study=study,
        )

        return {"study": study, "reference": reference}

    def test_assessment_systems(self):
        """Test that assessment_systems manager query returns count > 0 when data exists."""
        # Create assessment reference first
        self._setup_assessment_data()

        # Create terms associated with the assessment's study
        system_term = bake(
            Term,
            namespace=1,
            type=1,
            name="Cardiovascular",
            uid=5000
        )

        organ_term = bake(
            Term,
            namespace=1,
            type=2,
            name="Blood",
            parent_id=system_term.id,
            uid=5001
        )

        effect_term = bake(
            Term,
            namespace=1,
            type=3,
            name="Fatty Acids",
            parent_id=organ_term.id,
            uid=5002
        )

        endpoint_name_term = bake(
            Term,
            namespace=1,
            type=5,
            name="Lipid Profile",
            parent_id=effect_term.id,
            uid=5003
        )

        # Now test the manager - should return count > 0
        count = Term.objects.assessment_systems(self._setup_assessment_data()["reference"].assessment_id).count()
        
        assert count > 0

    def test_assessment_organs(self):
        """Test that assessment_organs manager query returns count > 0 when data exists."""
        self._setup_assessment_data()

        system_term = bake(
            Term,
            namespace=1,
            type=1,
            name="Cardiovascular",
            uid=6000
        )

        organ_term = bake(
            Term,
            namespace=1,
            type=2,
            name="Serum",
            parent_id=system_term.id,
            uid=6001
        )

        count = Term.objects.assessment_organs(self._setup_assessment_data()["reference"].assessment_id).count()
        
        assert count > 0

    def test_assessment_effects(self):
        """Test that assessment_effects manager query returns count > 0 when data exists."""
        self._setup_assessment_data()

        system_term = bake(
            Term,
            namespace=1,
            type=1,
            name="Hepatotoxicity",
            uid=6010
        )

        organ_term = bake(
            Term,
            namespace=1,
            type=2,
            name="Liver",
            parent_id=system_term.id,
            uid=6011
        )

        effect_term = bake(
            Term,
            namespace=1,
            type=3,
            name="Hepatocellular Injury",
            parent_id=organ_term.id,
            uid=6012
        )

        count = Term.objects.assessment_effects(self._setup_assessment_data()["reference"].assessment_id).count()
        
        assert count > 0

    def test_assessment_effect_subtypes(self):
        """Test that assessment_effect_subtypes manager query returns count > 0 when data exists."""
        self._setup_assessment_data()

        system_term = bake(
            Term,
            namespace=1,
            type=1,
            name="Nephrotoxicity",
            uid=6020
        )

        organ_term = bake(
            Term,
            namespace=1,
            type=2,
            name="Kidney",
            parent_id=system_term.id,
            uid=6021
        )

        effect_term = bake(
            Term,
            namespace=1,
            type=3,
            name="Acute Kidney Injury",
            parent_id=organ_term.id,
            uid=6022
        )

        subtype_term = bake(
            Term,
            namespace=1,
            type=4,
            name="Glomerular Filtration Rate",
            parent_id=effect_term.id,
            uid=6023
        )

        count = Term.objects.assessment_effect_subtypes(self._setup_assessment_data()["reference"].assessment_id).count()
        
        assert count > 0

    def test_assessment_endpoint_names(self):
        """Test that assessment_endpoint_names manager query returns count > 0 when data exists."""
        self._setup_assessment_data()

        system_term = bake(
            Term,
            namespace=1,
            type=1,
            name="Neurotoxicity",
            uid=6030
        )

        organ_term = bake(
            Term,
            namespace=1,
            type=2,
            name="Brain",
            parent_id=system_term.id,
            uid=6031
        )

        effect_term = bake(
            Term,
            namespace=1,
            type=3,
            name="Cognitive Impairment",
            parent_id=organ_term.id,
            uid=6032
        )

        endpoint_name_term = bake(
            Term,
            namespace=1,
            type=5,
            name="Working Memory Score",
            parent_id=effect_term.id,
            uid=6033
        )

        count = Term.objects.assessment_endpoint_names(self._setup_assessment_data()["reference"].assessment_id).count()
        
        assert count > 0

    def test_assessment_systems_no_data_returns_zero(self):
        """Test that assessment_systems returns 0 when no data exists."""
        # Don't create any terms - test should return 0
        count = Term.objects.assessment_systems(999).count()
        
        assert count == 0

    def test_assessment_organs_no_data_returns_zero(self):
        """Test that assessment_organs returns 0 when no data exists."""
        count = Term.objects.assessment_organs(998).count()
        
        assert count == 0

    def test_assessment_effects_no_data_returns_zero(self):
        """Test that assessment_effects returns 0 when no data exists."""
        count = Term.objects.assessment_effects(997).count()
        
        assert count == 0

    def test_assessment_effect_subtypes_no_data_returns_zero(self):
        """Test that assessment_effect_subtypes returns 0 when no data exists."""
        count = Term.objects.assessment_effect_subtypes(996).count()
        
        assert count == 0

    def test_assessment_endpoint_names_no_data_returns_zero(self):
        """Test that assessment_endpoint_names returns 0 when no data exists."""
        count = Term.objects.assessment_endpoint_names(995).count()
        
        assert count == 0

