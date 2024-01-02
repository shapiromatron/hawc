import pytest

from hawc.services.epa.dsstox import DssSubstance


@pytest.mark.vcr
class TestDssSubstance:
    def test_bad_dsstox(self):
        # test bad DTXSID
        with pytest.raises(ValueError) as err:
            DssSubstance.create_from_dtxsid("DTXSID123abc")
        assert str(err.value) == "Invalid DTXSID: DTXSID123abc"

        with pytest.raises(ValueError) as err:
            DssSubstance.create_from_dtxsid("DTXSID123456789")
        assert str(err.value) == "DTXSID123456789 not found in DSSTox lookup"

    def test_good_dsstox(self):
        # test success from DTXSID
        substance = DssSubstance.create_from_dtxsid("DTXSID7020970")
        assert substance.dtxsid == "DTXSID7020970"

    def test_fake(self, settings):
        settings.HAWC_FEATURES.FAKE_IMPORTS = True
        substance = DssSubstance.create_from_dtxsid("DTXSID123456")
        assert substance.content["preferredName"] == "Water"
        settings.HAWC_FEATURES.FAKE_IMPORTS = False
