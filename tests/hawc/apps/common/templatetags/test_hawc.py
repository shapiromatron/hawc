from hawc.apps.common.templatetags.hawc import hastext


class TestHasText:
    def test_hastext(self):
        for text in [None, "", "<p>  <br/>    \t</p>"]:
            assert hastext(text) is False
        for text in [0, False, "a", "&nbsp;", "<p>a</p>"]:
            assert hastext(text) is True
