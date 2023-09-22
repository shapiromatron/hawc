import pytest
from pydantic import ValidationError as PydanticError

from hawc.apps.common.dynamic_forms import Schema


class TestSchema:
    def test_field_validation(self):
        # all fields should have unique names
        schema_dict = {
            "fields": [
                {"name": "field1", "type": "char"},
                {"name": "field1", "type": "integer"},
            ]
        }
        with pytest.raises(PydanticError, match="Duplicate field name"):
            Schema.parse_obj(schema_dict)

        # all fields should have a valid type
        schema_dict = {
            "fields": [
                {"name": "field1"},
            ]
        }
        with pytest.raises(PydanticError, match="Discriminator 'type' is missing in value"):
            Schema.parse_obj(schema_dict)
        schema_dict = {
            "fields": [
                {"name": "field1", "type": "not a type"},
            ]
        }
        with pytest.raises(
            PydanticError,
            match="No match for discriminator 'type' and value 'not a type'",
        ):
            Schema.parse_obj(schema_dict)

        # if a widget is given, it should be valid for the type
        schema_dict = {
            "fields": [
                {"name": "field1", "type": "integer", "widget": "text_input"},
            ]
        }
        with pytest.raises(PydanticError, match="unexpected value; permitted: 'number_input'"):
            Schema.parse_obj(schema_dict)

    def test_condition_validation(self):
        # condition subjects should correspond with a field
        schema_dict = {
            "fields": [
                {"name": "field1", "type": "char"},
                {"name": "field2", "type": "char"},
                {"name": "field3", "type": "char"},
            ],
            "conditions": [
                {
                    "subject": "not_a_field",
                    "observers": ["field2", "field3"],
                    "comparison_value": "value",
                }
            ],
        }
        with pytest.raises(PydanticError, match="Invalid condition subject"):
            Schema.parse_obj(schema_dict)

        # condition observers should correspond with a field
        schema_dict = {
            "fields": [
                {"name": "field1", "type": "char"},
                {"name": "field2", "type": "char"},
                {"name": "field3", "type": "char"},
            ],
            "conditions": [
                {
                    "subject": "field1",
                    "observers": ["not_a_field", "field3"],
                    "comparison_value": "value",
                }
            ],
        }
        with pytest.raises(PydanticError, match="Invalid condition observer"):
            Schema.parse_obj(schema_dict)
