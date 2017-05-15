

from animal.forms import ExperimentForm
from utils.tests import FormTester

from . import utils


class ExperimentFormTester(FormTester):

    def setUp(self):
        self.Form = ExperimentForm
        self.baseInps = {
            'name': 'Example',
            'type': 'Ac',
            'litter_effects': 'NA',
            'purity_available': False,
            'purity_qualifier': "",
            'purity': None
        }
        utils.build_studies_for_permission_testing(self)

    def createTestForm(self, inps, *args, **kwargs):
        return self.Form(inps, parent=self.study_working)

    def test_valid_form(self):
        self.assertTrue(self.createTestForm(self.baseInps).is_valid())

    def test_purity(self):
        inps = self.baseInps.copy()

        inps.update(purity_available=True, purity=None, purity_qualifier="")
        self.fieldHasError(inps, "purity", self.Form.PURITY_REQ)
        self.fieldHasError(inps, "purity_qualifier", self.Form.PURITY_QUALIFIER_REQ)

        inps.update(purity_available=False, purity=95, purity_qualifier=">")
        self.fieldHasError(inps, "purity", self.Form.PURITY_NOT_REQ)
        self.fieldHasError(inps, "purity_qualifier", self.Form.PURITY_QUALIFIER_NOT_REQ)

    def test_litter_effects(self):
        inps = self.baseInps.copy()

        inps.update(type="Rp", litter_effects="NA")
        self.fieldHasError(inps, "litter_effects", self.Form.LIT_EFF_REQ)

        inps.update(type="Ac", litter_effects="NR")
        self.fieldHasError(inps, "litter_effects", self.Form.LIT_EFF_NOT_REQ)

        inps.update(type="Ac", litter_effects="NA", litter_effect_notes="Test")
        self.fieldHasError(inps, "litter_effect_notes",  self.Form.LIT_EFF_NOTES_NOT_REQ)

        inps.update(type="Rp", litter_effects="O", litter_effect_notes="")
        self.fieldHasError(inps, "litter_effect_notes",  self.Form.LIT_EFF_NOTES_REQ)
