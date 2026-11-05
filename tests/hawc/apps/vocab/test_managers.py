import pytest
from model_bakery.baker import make

from hawc.apps.animal.models import Study
from hawc.apps.vocab.models import Term


@pytest.mark.django_db
class TestTermManager:
    """Comprehensive tests for Term manager methods using manual test data creation."""

    def _setup_assessment_data(self):
        """Set up assessment data for manager tests."""

        study = make(Study)

        return {"study": study}

    def test_assessment_systems(self):
        """Test that assessment_systems manager query returns count > 0 when data exists."""
        # Create assessment reference first
        self._setup_assessment_data()

        # Create terms associated with the assessment's study
        system_term = make(Term, namespace=1, type=1, name="Cardiovascular", uid=5000)

        organ_term = make(
            Term, namespace=1, type=2, name="Blood", parent_id=system_term.id, uid=5001
        )

        effect_term = make(
            Term, namespace=1, type=3, name="Fatty Acids", parent_id=organ_term.id, uid=5002
        )

        endpoint_name_term = make(
            Term, namespace=1, type=5, name="Lipid Profile", parent_id=effect_term.id, uid=5003
        )

        # Now test the manager - should return count > 0
        count = Term.objects.assessment_systems(
            self._setup_assessment_data()["study"].assessment_id
        ).count()

        assert count > 0

    def test_assessment_organs(self):
        """Test that assessment_organs manager query returns count > 0 when data exists."""
        self._setup_assessment_data()

        system_term = make(Term, namespace=1, type=1, name="Cardiovascular", uid=6000)

        organ_term = make(
            Term, namespace=1, type=2, name="Serum", parent_id=system_term.id, uid=6001
        )

        count = Term.objects.assessment_organs(
            self._setup_assessment_data()["study"].assessment_id
        ).count()

        assert count > 0

    def test_assessment_effects(self):
        """Test that assessment_effects manager query returns count > 0 when data exists."""
        self._setup_assessment_data()

        system_term = bake(Term, namespace=1, type=1, name="Hepatotoxicity", uid=6010)

        organ_term = bake(
            Term, namespace=1, type=2, name="Liver", parent_id=system_term.id, uid=6011
        )

        effect_term = bake(
            Term,
            namespace=1,
            type=3,
            name="Hepatocellular Injury",
            parent_id=organ_term.id,
            uid=6012,
        )

        count = Term.objects.assessment_effects(
            self._setup_assessment_data()["study"].assessment_id
        ).count()

        assert count > 0

    def test_assessment_effect_subtypes(self):
        """Test that assessment_effect_subtypes manager query returns count > 0 when data exists."""
        self._setup_assessment_data()

        system_term = bake(Term, namespace=1, type=1, name="Nephrotoxicity", uid=6020)

        organ_term = bake(
            Term, namespace=1, type=2, name="Kidney", parent_id=system_term.id, uid=6021
        )

        effect_term = bake(
            Term, namespace=1, type=3, name="Acute Kidney Injury", parent_id=organ_term.id, uid=6022
        )

        subtype_term = bake(
            Term,
            namespace=1,
            type=4,
            name="Glomerular Filtration Rate",
            parent_id=effect_term.id,
            uid=6023,
        )

        count = Term.objects.assessment_effect_subtypes(
            self._setup_assessment_data()["study"].assessment_id
        ).count()

        assert count > 0

    def test_assessment_endpoint_names(self):
        """Test that assessment_endpoint_names manager query returns count > 0 when data exists."""
        self._setup_assessment_data()

        system_term = bake(Term, namespace=1, type=1, name="Neurotoxicity", uid=6030)

        organ_term = bake(
            Term, namespace=1, type=2, name="Brain", parent_id=system_term.id, uid=6031
        )

        effect_term = bake(
            Term,
            namespace=1,
            type=3,
            name="Cognitive Impairment",
            parent_id=organ_term.id,
            uid=6032,
        )

        endpoint_name_term = bake(
            Term,
            namespace=1,
            type=5,
            name="Working Memory Score",
            parent_id=effect_term.id,
            uid=6033,
        )

        count = Term.objects.assessment_endpoint_names(
            self._setup_assessment_data()["study"].assessment_id
        ).count()

        assert count > 0
