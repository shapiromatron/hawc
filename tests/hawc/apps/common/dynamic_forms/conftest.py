import pytest


@pytest.fixture()
def complete_schema() -> dict:
    return {
        "fields": [
            {
                "name": "textbox",
                "type": "char",
                "required": False,
                "help_text": "Help text",
                "css_class": "col-3",
            },
            {
                "name": "checkbox",
                "type": "boolean",
                "required": False,
                "help_text": "Help text",
                "css_class": "col-3",
            },
            {
                "name": "integer",
                "type": "integer",
                "required": False,
                "help_text": "Help text",
                "css_class": "col-3",
            },
            {
                "name": "float",
                "type": "float",
                "required": False,
                "help_text": "Help text",
                "css_class": "col-3",
            },
            {
                "name": "select",
                "type": "choice",
                "choices": [["1", "Item 1"], ["2", "Item 2"], ["3", "Item 3"]],
                "required": False,
                "help_text": "Help text",
                "css_class": "col-6",
            },
            {
                "name": "select_multiple",
                "type": "multiple_choice",
                "choices": [["1", "Item 1"], ["2", "Item 2"], ["3", "Item 3"]],
                "required": False,
                "help_text": "Help text",
                "css_class": "col-6",
            },
            {
                "name": "radio",
                "type": "choice",
                "widget": "radio_select",
                "choices": [["1", "Item 1"], ["2", "Item 2"], ["3", "Item 3"]],
                "required": False,
                "help_text": "Help text",
                "css_class": "col-6",
            },
            {
                "name": "yesno",
                "type": "yes_no",
                "label": "Yes/no field?",
                "required": False,
                "help_text": "Help text",
                "css_class": "col-6",
            },
            {
                "name": "checkbox_multiple",
                "type": "multiple_choice",
                "widget": "checkbox_select_multiple",
                "choices": [["1", "Item 1"], ["2", "Item 2"], ["3", "Item 3"]],
                "required": False,
                "help_text": "Help text",
                "css_class": "col-6",
            },
        ],
        "conditions": [],
    }
