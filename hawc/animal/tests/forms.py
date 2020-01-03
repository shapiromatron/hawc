from animal.forms import ExperimentForm
from utils.tests import FormTester

from . import utils


class ExperimentFormTester(FormTester):

    def setUp(self):
        self.Form = ExperimentForm
        self.baseInps = {
            'name': 'Example',
            'type': 'Ac',
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
