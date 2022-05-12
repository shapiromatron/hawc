import re
from pathlib import Path

from django.conf import settings


def _remove_spacing(txt, character):
    txt = re.sub(character + " ", character, txt)
    return re.sub(" " + character, character, txt)


def _compact(txt):
    txt = re.sub(r"\/\*[^(\*\/)]+\*\/", " ", txt)
    txt = re.sub(r"\n", " ", txt)
    txt = re.sub(r" >", " ", txt)  # can break illustrator
    txt = re.sub(r"[ ]+", " ", txt)
    txt = _remove_spacing(txt, ":")
    txt = _remove_spacing(txt, "{")
    txt = _remove_spacing(txt, "}")
    txt = _remove_spacing(txt, ";")
    return txt


def get_styles_svg_definition():
    """
    Return CSS styles for embedding into an SVG document
    """
    styles = Path(settings.PROJECT_PATH / "static/css/d3.css").read_text()
    compact_styles = _compact(styles)
    return f'<defs><style type="text/css"><![CDATA[{compact_styles}]]></style></defs>'
