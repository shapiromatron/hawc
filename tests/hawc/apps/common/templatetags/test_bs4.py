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


@pytest.mark.parametrize(
    "input, output",
    [
        (
            "{% load bs4 %}{% alert %}🙂{% endalert %}",
            '<div class="alert alert-danger ">🙂</div>',
        ),
        (
            '{% load bs4 %}{% alert type="info" classes="foo" %}🙂{% endalert %}',
            '<div class="alert alert-info foo">🙂</div>',
        ),
        (
            "{% load bs4 %}{% alert dismiss=True %}🙂{% endalert %}",
            '<div class="alert alert-danger "><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>🙂</div>',
        ),
    ],
)
def test_bs4_alert(input, output):
    assert Template(input).render(Context({})) == output
