import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from shutil import which

import pytest

from hawc.apps.common.svg import SVGConverter

DATA_PATH = Path(__file__).parent.absolute() / "data"


@pytest.mark.skipif(which("phantomjs") is None, reason="requires phantomjs on path to run")
class TestSvgConverter:
    def test_svg(self, svg_data):
        conv = SVGConverter(*svg_data)
        resp = conv.to_svg()

        # svg can be parsed
        tree = ET.fromstring(resp)

        # we have defs added
        defs = tree.find(".{http://www.w3.org/2000/svg}defs")
        assert defs is not None

        # we have styles added and the text is non-empty
        styles = tree.find(".{http://www.w3.org/2000/svg}defs/{http://www.w3.org/2000/svg}style")
        assert styles.attrib["type"] == "text/css"
        assert styles is not None and len(styles.text) > 0

        # and we still have our rect
        rect = tree.find(".{http://www.w3.org/2000/svg}rect")
        assert rect is not None

    def test_png(self, svg_data):
        conv = SVGConverter(*svg_data)
        resp = conv.to_png()
        assert isinstance(resp, bytes)
        assert (DATA_PATH / "svg-converter.png").read_bytes() == resp

    def test_pdf(self, svg_data):
        conv = SVGConverter(*svg_data)
        resp = conv.to_pdf()
        assert isinstance(resp, bytes)
        # can't compare file; timestamp metadata information pdf

    def test_pptx(self, svg_data):
        conv = SVGConverter(*svg_data)
        resp = conv.to_pptx()
        assert isinstance(resp, BytesIO)
        # can't compare file; timestamp metadata information pptx

    def test_decode_svg(self, svg_data):
        # success
        data = SVGConverter.decode_svg(svg_data[0])
        assert data.startswith("<svg")

        # failures
        for value in ["💥", "�", "/../../WEB-INF/web.xml"]:
            with pytest.raises(ValueError):
                SVGConverter.decode_svg(value)
