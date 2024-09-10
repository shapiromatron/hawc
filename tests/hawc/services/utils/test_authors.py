from hawc.services.utils.authors import get_author_short_text, get_first, normalize_author


class TestNormalizeAuthors:
    def test_expected(self):
        # test no initials
        assert normalize_author("Smith") == "Smith"
        assert normalize_author("Smith") == "Smith"
        assert normalize_author("Smith, Kevin") == "Smith Kevin"
        assert normalize_author("Smith, Kevin James") == "Smith Kevin James"
        assert normalize_author("Smith, Kevin J.") == "Smith Kevin J"

        # test no periods
        assert normalize_author("Smith K") == "Smith K"
        assert normalize_author("Smith, K") == "Smith K"
        assert normalize_author("Smith KJ") == "Smith KJ"
        assert normalize_author("Smith, KJ") == "Smith KJ"
        assert normalize_author("Smith K J") == "Smith KJ"
        assert normalize_author("Smith, K J") == "Smith KJ"

        # test w/ periods
        assert normalize_author("Smith K.") == "Smith K"
        assert normalize_author("Smith, K.") == "Smith K"
        assert normalize_author("Smith K.J.") == "Smith KJ"
        assert normalize_author("Smith, K.J.") == "Smith KJ"
        assert normalize_author("Smith K. J.") == "Smith KJ"
        assert normalize_author("Smith, K. J.") == "Smith KJ"

        # hyphenated
        assert normalize_author("Smith-Hyphenated, Kevin") == "Smith-Hyphenated Kevin"

        # unicode
        assert normalize_author("Langkjær, Svend") == "Langkjær Svend"
        assert normalize_author("Åmith K.") == "Åmith K"
        assert normalize_author("Åmith Å. Å.") == "Åmith ÅÅ"
        assert normalize_author("Åmith K.") == "Åmith K"

        # not an author-like name
        assert (
            normalize_author("The National Academies of Sciences, Engineering, and Medicine")
            == "The National Academies of Sciences, Engineering, and Medicine"
        )

    def test_edges(self):
        assert normalize_author("") == ""
        assert normalize_author("SKJ") == "SKJ"


def test_get_author_short_text():
    # 0 test
    assert get_author_short_text([]) == ""

    # 1 test
    assert get_author_short_text(["Smith J"]) == "Smith J"

    # 2 test
    assert get_author_short_text(["Smith J"] * 2) == "Smith J and Smith J"

    # 3 test
    assert get_author_short_text(["Smith J"] * 3) == "Smith J, Smith J, and Smith J"

    # 4 test
    assert get_author_short_text(["Smith J"] * 4) == "Smith J et al."


def test_get_first():
    assert get_first({"foo": 1}, ["foo"]) == 1
    assert get_first({"foo": 1}, ["bar", "foo"]) == 1
    assert get_first({"foo": 1}, ["baz"]) is None
    assert get_first({"foo": 1}, ["baz"], -9999) == -9999
