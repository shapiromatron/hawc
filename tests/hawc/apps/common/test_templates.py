from django.core.exceptions import ValidationError
from django.template import Context, Template


def test_error_list():
    template = Template("{% include 'common/fragments/error_list.html' %}")

    # ValueError
    err = ValueError("This is a value error")
    rendered = template.render(Context({"err": err}))
    assert "<li>This is a value error</li>" in rendered

    # ValidationError
    err = ValidationError({"__all__": ["Error A", "Error B"], "field1": ["Error C"]})
    rendered = template.render(Context({"err": err}))
    assert "<strong>Overall:</strong>" in rendered
    assert "__all__" not in rendered
    assert "Error A" in rendered
    assert "<strong>field1:</strong>" in rendered
    assert "Error C" in rendered
