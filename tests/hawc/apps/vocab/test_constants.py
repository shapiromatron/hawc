import pytest

from hawc.apps.vocab.constants import VocabularyNamespace, VocabularyTermType


class TestVocabularyNamespace:
    def test_display_choices(self):
        assert VocabularyNamespace.display_choices() == [
            (1, "EPA Environmental health vocabulary"),
            (2, "EPA ToxRefDB vocabulary"),
        ]

    @pytest.mark.parametrize(
        ("obj", "value"),
        [
            (VocabularyNamespace.EHV, "EPA Environmental health vocabulary"),
            (VocabularyNamespace.ToxRefDB, "EPA ToxRefDB vocabulary"),
        ],
    )
    def test_display_name(self, obj: VocabularyNamespace, value):
        assert obj.display_name == value

    @pytest.mark.parametrize(
        ("obj", "url"),
        [
            (VocabularyNamespace.EHV, "/vocab/ehv/"),
            (VocabularyNamespace.ToxRefDB, "/vocab/toxrefdb/"),
        ],
    )
    def test_display_url(self, obj: VocabularyNamespace, url):
        assert obj.display_url == url


class TestVocabularyTermType:
    def test_value_to_text_field(self):
        mapping = VocabularyTermType.value_to_text_field()
        assert mapping[VocabularyTermType.system] == VocabularyTermType.system.name
        assert mapping[VocabularyTermType.endpoint_name] == "name"

    def test_value_to_term_field(self):
        mapping = VocabularyTermType.value_to_term_field()
        assert mapping[VocabularyTermType.system] == "system_term_id"
        assert mapping[VocabularyTermType.endpoint_name] == "name_term_id"
