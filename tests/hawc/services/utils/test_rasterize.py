import base64
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from shutil import which

import pytest

from hawc.services.utils.rasterize import SVGConverter

DATA_PATH = Path(__file__).parent.absolute() / "data"


@pytest.fixture
def svg_data():
    svg = """<svg width="100" height="100" version="1.1" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="10" width="80" height="80" style="fill:red;stroke-width:3;stroke:blue" />
        </svg>"""
    return (svg, "/test/", 240, 240)


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
        data = SVGConverter.decode_svg(base64.encodebytes(svg_data[0].encode()))
        assert data.startswith("<svg")

        # failures
        for value in [
            "not b64",
            "/../../WEB-INF/web.xml",
            "💥",
            base64.encodebytes(b"Valid b64; not SVG"),
            base64.encodebytes(b"<p>Not an SVG</p>"),
        ]:
            with pytest.raises(ValueError):
                SVGConverter.decode_svg(value)
