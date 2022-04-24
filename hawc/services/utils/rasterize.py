import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)


class HawcStyles:
    @property
    def for_svg(self):
        # lazy evaluation
        style = getattr(self, "_for_svg", None)
        if style is None:
            style = f'<defs><style type="text/css"><![CDATA[{self._get_styles()}]]></style></defs>'
            setattr(self, "_for_svg", style)
        return style

    def _get_styles(self):
        def remove_spacing(txt, character):
            txt = re.sub(character + " ", character, txt)
            return re.sub(" " + character, character, txt)

        def get_styles(fn):
            # Only using D3.css as adding other style-sheets with non SVG
            # styles can potentially break the SVG processor.
            texts = []
            with open(fn, "r") as f:
                texts.append(f.read())
            return " ".join(texts)

        def compact(txt):
            txt = re.sub(r"\/\*[^(\*\/)]+\*\/", " ", txt)
            txt = re.sub(r"\n", " ", txt)
            txt = re.sub(r" >", " ", txt)  # can break illustrator
            txt = re.sub(r"[ ]+", " ", txt)
            txt = remove_spacing(txt, ":")
            txt = remove_spacing(txt, "{")
            txt = remove_spacing(txt, "}")
            txt = remove_spacing(txt, ";")
            txt = re.sub(r"}", r"}\n", txt)
            return txt

        css_file = str(settings.PROJECT_PATH / "static/css/d3.css")
        return compact(get_styles(css_file))


Styles = HawcStyles()
