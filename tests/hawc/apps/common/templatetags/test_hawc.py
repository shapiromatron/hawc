from hawc.apps.common.templatetags.hawc import e_notation, hastext


class TestHasText:
    def test_hastext(self):
        for text in [None, "", "<p>  <br/>    \t</p>"]:
            assert hastext(text) is False
        for text in [0, False, "a", "&nbsp;", "<p>a</p>"]:
            assert hastext(text) is True


class TestENotation:
    def test_e_notation(self):
        assert e_notation(1) == 1
        assert e_notation(0.0009) == " 9.00e-04"
        assert e_notation(0.0000001) == " 1e-07"
        assert e_notation(100000) == 100000
