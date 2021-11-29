from hawc.services.utils.doi import (
    get_doi_from_hero,
    get_doi_from_pubmed,
    get_doi_from_ris,
    get_doi_if_valid,
)


class TestGetDoiValid:
    def test_valid(self):
        assert (
            get_doi_if_valid("10.1016/j.anifeedsci.2017.11.014")
            == "10.1016/j.anifeedsci.2017.11.014"
        )
        assert (
            get_doi_if_valid(" 10.1016/j.anifeedsci.2017.11.014 ")
            == "10.1016/j.anifeedsci.2017.11.014"
        )
        assert (
            get_doi_if_valid("before10.1016/j.anifeedsci.2017.11.014</ArticleId>")
            == "10.1016/j.anifeedsci.2017.11.014"
        )
        assert (
            get_doi_if_valid("before10.1016/j.anifeedsci.2017.11.014</ELocationID>")
            == "10.1016/j.anifeedsci.2017.11.014"
        )
        assert (
            get_doi_if_valid("10.1043/1543-2165(2005)129&lt;0632:swphea&gt;2.0.co;2")
            == "10.1043/1543-2165(2005)129<0632:swphea>2.0.co;2"
        )
        assert (
            get_doi_if_valid("10.1044/1092-4388%282009/08-0116%29")
            == "10.1044/1092-4388(2009/08-0116)"
        )
        assert get_doi_if_valid("doi:10.1037/arc0000014") == "10.1037/arc0000014"
        assert get_doi_if_valid("https://doi.org/10.1037/arc0000014.") == "10.1037/arc0000014"
        assert get_doi_if_valid("http://dx.doi.org/10.1037/arc0000014") == "10.1037/arc0000014"
        assert (
            get_doi_if_valid(
                "before10.1002/%28sici%291096-9926%28199711%2956:5&lt;311::aid-tera4&gt;3.0.co;2-#</ArticleId>"
            )
            == "10.1002/(sici)1096-9926(199711)56:5<311::aid-tera4>3.0.co;2-#"
        )

    def test_invalid(self):
        assert get_doi_if_valid("") == None
        assert get_doi_if_valid("10.") == None
        assert get_doi_if_valid("10") == None
        assert get_doi_if_valid("1") == None
        assert get_doi_if_valid("trust me, im a doi") == None
        assert get_doi_if_valid("10.123/141414141") == None
