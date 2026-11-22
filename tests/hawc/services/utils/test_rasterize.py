import pytest

from hawc.services.utils import rasterize


@pytest.mark.parametrize(
    ("css", "expected"),
    [
        ("a { color: red; }", "a{color:red;}"),
        ("/* comment */a {\n  top: 0;\n}", " a{top:0;}"),
        ("a > b {top: 1}", "a b{top:1}"),
    ],
)
def test_compact(css, expected):
    assert rasterize._compact(css) == expected


def test_get_styles_svg_definition():
    definition = rasterize.get_styles_svg_definition()
    assert definition.startswith('<defs><style type="text/css"><![CDATA[')
    assert definition.endswith("]]></style></defs>")
    assert "\n" not in definition
