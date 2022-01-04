from hawc.services.utils.doi import try_get_doi


class TestTryGetDoi:
    def test_valid(self):
        # not full-text
        assert try_get_doi("10.1016/j.anifeedsci.2017.11.014") == "10.1016/j.anifeedsci.2017.11.014"
        assert (
            try_get_doi(" 10.1016/j.anifeedsci.2017.11.014 ") == "10.1016/j.anifeedsci.2017.11.014"
        )
        assert (
            try_get_doi("10.1043/1543-2165(2005)129&lt;0632:swphea&gt;2.0.co;2")
            == "10.1043/1543-2165(2005)129<0632:swphea>2.0.co;2"
        )
        assert (
            try_get_doi("10.1044/1092-4388%282009/08-0116%29") == "10.1044/1092-4388(2009/08-0116)"
        )
        assert try_get_doi("doi:10.1037/arc0000014") == "10.1037/arc0000014"
        assert try_get_doi("http://dx.doi.org/10.1037/arc0000014") == "10.1037/arc0000014"

        # from full-text
        assert (
            try_get_doi('https://doi.org/10.1037/arc0000014,".', full_text=True)
            == "10.1037/arc0000014"
        )
        assert (
            try_get_doi("https://doi.org/10.1037/arc0000014.", full_text=True)
            == "10.1037/arc0000014"
        )
        assert (
            try_get_doi("before10.1016/j.anifeedsci.2017.11.014</ArticleId>", full_text=True)
            == "10.1016/j.anifeedsci.2017.11.014"
        )
        assert (
            try_get_doi("before10.1016/j.anifeedsci.2017.11.014</ELocationID>", full_text=True)
            == "10.1016/j.anifeedsci.2017.11.014"
        )
        assert (
            try_get_doi(
                "before10.1002/%28sici%291096-9926%28199711%2956:5&lt;311::aid-tera4&gt;3.0.co;2-#</ArticleId>",
                full_text=True,
            )
            == "10.1002/(sici)1096-9926(199711)56:5<311::aid-tera4>3.0.co;2-#"
        )

    def test_invalid(self):
        assert try_get_doi("") is None
        assert try_get_doi("10.") is None
        assert try_get_doi("10") is None
        assert try_get_doi("1") is None
        assert try_get_doi("trust me, im a doi") is None
        assert try_get_doi("10.123/141414141") is None
