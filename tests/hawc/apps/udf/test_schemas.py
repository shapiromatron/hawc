import pytest
from pydantic import ValidationError

from hawc.apps.udf import schemas


@pytest.fixture
def valid_tag_content():
    return {
        "assessment": 4,
        "tag_binding": 1,
        "reference": 13,
        "content": {"field1": "updated data", "field2": 1234},
    }


@pytest.mark.django_db
class TestModifyTagUDFContent:
    def test_success(self, valid_tag_content):
        schemas.ModifyTagUDFContent.model_validate(valid_tag_content)

    def test_check_objects(self, valid_tag_content):
        data = valid_tag_content.copy()
        data["tag_binding"] = 99999
        with pytest.raises(ValidationError, match="Tag binding not found"):
            schemas.ModifyTagUDFContent.model_validate(data)

        data = valid_tag_content.copy()
        data["reference"] = 999999
        with pytest.raises(ValidationError, match="Reference not found"):
            schemas.ModifyTagUDFContent.model_validate(data)

        data = valid_tag_content.copy()
        data["content"] = {}
        with pytest.raises(ValidationError, match="This field is required"):
            schemas.ModifyTagUDFContent.model_validate(data)


@pytest.fixture
def valid_model_content():
    return {
        "assessment": 4,
        "content_type": "study.study",
        "object_id": 9,
        "content": {"field1": "updated data", "field2": 1234},
    }


@pytest.mark.django_db
class TestModifyModelUDFContent:
    def test_success(self, valid_model_content):
        schemas.ModifyModelUDFContent.model_validate(valid_model_content)

    def test_ct_format(self, valid_model_content):
        for failure in ["foo", "foo.foo.foo"]:
            data = valid_model_content.copy()
            data["content_type"] = failure
            with pytest.raises(ValidationError, match="Must provide a content_type in the form"):
                schemas.ModifyModelUDFContent.model_validate(data)

    def test_check_objects(self, valid_model_content):
        data = valid_model_content.copy()
        data["content_type"] = "foo.foo"
        with pytest.raises(ValidationError, match="Content type not found"):
            schemas.ModifyModelUDFContent.model_validate(data)

        data = valid_model_content.copy()
        data["object_id"] = 999999
        with pytest.raises(ValidationError, match="Object not found"):
            schemas.ModifyModelUDFContent.model_validate(data)

        data = valid_model_content.copy()
        data["content"] = {}
        with pytest.raises(ValidationError, match="This field is required"):
            schemas.ModifyModelUDFContent.model_validate(data)
