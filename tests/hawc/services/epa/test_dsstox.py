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
        assert str(err.value) == "Chemical identifier DTXSID123456789 not found in DSSTox lookup"

    def test_good_dsstox(self):
        # test success from CASRN
        substance = DssSubstance.create_from_identifier("1836-75-5")
        assert substance.dtxsid == "DTXSID7020970"

        # test success from DTXSID
        substance = DssSubstance.create_from_dtxsid("DTXSID7020970")
        assert substance.dtxsid == "DTXSID7020970"
