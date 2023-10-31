from copy import deepcopy

from crispy_forms.utils import render_crispy_form
from pytest_django.asserts import assertInHTML

from hawc.apps.common.dynamic_forms import Schema


class TestDynamicForm:
    def test_field_rendering(self, complete_schema):
        # ensure schema with all field types can render without error
        schema = Schema.parse_obj(complete_schema)
        form_rendering = render_crispy_form(schema.to_form({}))
        assert len(form_rendering) > 0

    def test_yesno_rendering(self, complete_schema):
        # ensure yesno field with inline styles renders as expected
        yesno = deepcopy(complete_schema)
        yesno["fields"] = [field for field in yesno["fields"] if field["name"] == "yesno"]
        schema = Schema.parse_obj(yesno)
        form_rendering = render_crispy_form(schema.to_form({}))
        expected = """<div class="form-row ">
        <div \n class="col-6">
        <div id="div_id_yesno" class="form-group"> <label class="">\n Yes/no field?\n </label>
        <div><div class="custom-control custom-radio custom-control-inline"> <input type="radio"
        class="custom-control-input" name="yesno" value="yes" id="id_yesno_0" \n> <label
        class="custom-control-label" for="id_yesno_0">\n Yes\n </label> </div>
        <div class="custom-control custom-radio custom-control-inline"> <input type="radio"
        class="custom-control-input" name="yesno" value="no" id="id_yesno_1" \n> <label
        class="custom-control-label" for="id_yesno_1">\n No\n </label> </div> <small id="hint_id_yesno"
        class="form-text text-muted">Help text</small>
        </div></div></div></div>"""
        assertInHTML(expected, form_rendering)

    def test_validation(self):
        schema_dict = {"fields": [{"name": "integer", "type": "integer", "required": True}]}
        schema = Schema.parse_obj(schema_dict)
        # check required
        form_data = {}
        form = schema.to_form(form_data)
        assert form.errors == {"integer": ["This field is required."]}
        # check types
        form_data = {"integer": "text"}
        form = schema.to_form(form_data)
        assert form.errors == {"integer": ["Enter a whole number."]}

    def test_conditions(self):
        schema_dict = {
            "fields": [
                {"name": "field1", "type": "char", "required": True},
                {"name": "field2", "type": "char", "required": True},
                {"name": "field3", "type": "char", "required": True},
            ],
            "conditions": [
                {
                    "subject": "field1",
                    "observers": ["field2", "field3"],
                    "comparison": "equals",
                    "comparison_value": "value",
                    "behavior": "hide",
                }
            ],
        }
        schema = Schema.parse_obj(schema_dict)
        # required should remain required when shown
        form_data = {"field1": "not value"}
        form = schema.to_form(form_data)
        assert "field2" in form.errors
        assert "field3" in form.errors
        # required should become optional when hidden
        form_data = {"field1": "value"}
        form = schema.to_form(form_data)
        assert form.is_valid()
        # hidden fields are left out of data
        form_data = {"field1": "value", "field2": "hidden", "field3": "hidden"}
        form = schema.to_form(form_data)
        assert form.is_valid()
        assert form.cleaned_data == {"field1": "value"}
