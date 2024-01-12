import pytest
from django.template import Context, Template


@pytest.mark.parametrize(
    "input, conj, expected",
    [
        (["a"], "", "a"),
        (["a", "b"], "", "a or b"),
        (["a", "b"], "'and'", "a and b"),
        (["a", "b", "c"], "", "a, b, or c"),
        (["a", "b", "c"], "'and'", "a, b, and c"),
    ],
)
def test_list_punctuation(input, conj, expected):
    template_to_render = "{% load bs4 %}{% for item in items %}{{item}}{% list_punctuation forloop ZZZ %}{% endfor %}"
    rendered_template = Template(template_to_render.replace("ZZZ", conj)).render(
        Context({"items": input})
    )
    assert rendered_template.strip() == expected
