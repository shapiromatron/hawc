import pytest

from hawc.apps.udf.models import ModelUDFContent, UserDefinedForm


class TestUserDefinedForm:
    def test_validate_data(self):
        udf = UserDefinedForm(schema={"fields": [{"name": "field", "type": "integer"}]})
        for data in [{}, {"field": "test"}]:
            with pytest.raises(ValueError):
                udf.validate_data(data)
        assert udf.validate_data({"field": 123}) is None


@pytest.mark.django_db
class TestModelUDFContent:
    def test_get_content_as_list(self):
        content = ModelUDFContent.objects.get(id=1)
        assert content.get_content_as_list() == [("Field1", "test"), ("Field2", 123)]

    def test_get_instance(self):
        content = ModelUDFContent.objects.get(id=1)
        assert (
            content.get_instance(content.content_object.assessment, content.content_object)
            == content
        )
