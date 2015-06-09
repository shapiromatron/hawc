from __future__ import absolute_import
from datetime import datetime
import codecs
import os
import random
import re
import string
import subprocess
from StringIO import StringIO
import urllib2
import xml.etree.ElementTree as ET

from django.conf import settings
from django.core.cache import cache

from celery import shared_task
from celery.utils.log import get_task_logger
import requests
from pptx import Presentation
from pptx.util import Inches, Pt


logger = get_task_logger(__name__)


# load CSS into memory upon runtime (only do it once)
D3_CSS_STYLES = u""
D3_CSS_PATH = os.path.abspath(
    os.path.join(settings.PROJECT_PATH,
                 r'static/css/hawc_d3_aggregated.css'))
if os.path.exists(D3_CSS_PATH):
    with codecs.open(D3_CSS_PATH, 'r', 'UTF-8') as f:
        D3_CSS_STYLES = unicode(f.read())


class SVGConverter():

    def __init__(self, svg, url=None, width=None, height=None):
        self.inkscape = settings.INKSCAPE
        self.temp_path = settings.TEMP_PATH
        self.url = url
        self.width = width
        self.height = height
        self.svg = self._process_svg(svg)

    def _process_svg(self, svg):
        """
        CSS styles must be manually added to the SVG object; after trying
        numerous tools they couldn't reliably get the information from the
        browser. Thus, we load a predefined set of styles created using the
        stylesheets.
        """
        # decode from base64 and convert unicode characters
        svg = svg.decode('base64').replace('%u', '\\u').decode('unicode_escape')
        svg = urllib2.unquote(svg)

        # add CSS styles
        matches = re.finditer(ur'<svg [^>]+>', svg)
        for m in matches:
            insertion_point = m.end()

        #Manually add our CSS styles from a file. Because there are problems
        # inserting CDATA using a python etree, we use a regex instead
        svg = (svg[:insertion_point] +
               r'<defs style="hawc-styles"><style type="text/css"><![CDATA[{css}]]></style></defs>'.format(css=D3_CSS_STYLES) +
               svg[insertion_point:])

        return svg

    def get_svg(self):
        return self.svg

    def _try_to_remove_files(self, files):
        # try to remove files in list of files
        for f in files:
            try:
                os.remove(f)
            except:
                pass

    def _save_svg(self, output_extension=''):
        # return input and output filename and save svg to disk
        fn = ''.join(random.choice(string.ascii_lowercase) for x in range(16))
        fn_in = os.path.join(self.temp_path, fn + '.svg')
        fn_out = os.path.join(self.temp_path, fn + output_extension)

        with open(fn_in, 'w') as f:
            f.write(self.svg.encode('utf-8'))

        return (fn_in, fn_out)

    @shared_task
    def convert_to_png(self, delete_and_return_object=True):
        """
        Given an svg data object, convert to a png object, and return the
        status of if conversion was successful and the object if complete. Uses
        Inkscape to convert, requires writing files to disk.
        """
        logger.info('Converting svg to png')
        png = None

        try:
            (fn_in, fn_out) = self._save_svg(output_extension='.png')
            export_tag = '--export-png={f}'.format(f=fn_out)
            width_tag = '--export-width={f}'.format(f=self.width) if self.width else ''
            height_tag = '--export-height={f}'.format(f=self.height) if self.height else ''
            background = '--export-background=white'
            commands = [self.inkscape, fn_in, export_tag, background, width_tag, height_tag]
            subprocess.call(commands, cwd=self.temp_path)
            logger.info('Conversion successful')

        except Exception as e:
            logger.error(e.message, exc_info=True)
            return None

        if delete_and_return_object:
            if os.path.exists(fn_out):
                png = open(fn_out, 'rb').read()
            self._try_to_remove_files([fn_in, fn_out])
            return png
        else:
            self._try_to_remove_files([fn_in])
            self.png_path = fn_out
            return self

    @shared_task
    def convert_to_pptx(self):
        logger.info('Converting svg to pptx')
        pptx = None

        try:
            # get converted png image path
            fn_png = self.png_path

            # create blank presentation slide layout
            prs = Presentation()
            blank_slidelayout = prs.slide_layouts[6]
            slide = prs.slides.add_slide(blank_slidelayout)

            # add title
            txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(9), Inches(0.5))
            tf = txBox.textframe
            now = datetime.now().strftime("%B %d %Y, %I:%M %p")
            tf.text = "HAWC visualization generated on {now}".format(now=now)
            tf.paragraphs[0].alignment = 2

            # add website address
            txBox = slide.shapes.add_textbox(Inches(0), Inches(7.0), Inches(10), Inches(0.5))
            tf = txBox.textframe
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = self.url
            run.hyperlink.address = self.url
            p.font.size = Pt(12)
            p.alignment = 2

            # add picture, after getting proper dimensions
            max_height = 6.
            max_width = 9.
            left = Inches(0.5)
            top = Inches(0.75)
            width_to_height_ratio = float(self.width)/self.height
            if width_to_height_ratio > (max_width/max_height):
                width = Inches(max_width)
                height = width/width_to_height_ratio
                top = top + int((Inches(max_height)-height)*0.5)
            else:
                height = Inches(max_height)
                width = height*width_to_height_ratio
                left = left + int((Inches(max_width)-width)*0.5)

            slide.shapes.add_picture(fn_png, left, top, width, height)

            # add HAWC logo
            left = Inches(9.5)
            top = Inches(7)
            width = Inches(0.5)
            height = Inches(0.5)
            logo_location = os.path.join(settings.STATIC_ROOT, "img/hawc.png")
            slide.shapes.add_picture(logo_location, left, top, width, height)

            # save as object
            output = StringIO()
            prs.save(output)
            output.seek(0)

            # remove png file from disk
            self._try_to_remove_files([fn_png])

            pptx = output
            logger.info('Conversion successful')

        except Exception as e:
            logger.error(e.message, exc_info=True)

        return pptx

    @shared_task
    def convert_to_pdf(self):
        """
        Given an svg data object, convert to a pdf object, and return the
        status of if conversion was successful and the object if complete.
        Uses Inkscape to convert, requires writing files to disk.
        """
        logger.info('Converting svg to pdf')
        pdf = None

        try:
            (fn_in, fn_out) = self._save_svg(output_extension='.pdf')
            export_tag = '--export-pdf=' + fn_out
            commands = [self.inkscape, fn_in, export_tag]
            subprocess.call(commands, cwd=self.temp_path)
            logger.info('Conversion successful')
        except Exception as e:
            logger.error(e.message, exc_info=True)
            return None

        if os.path.exists(fn_out):
            pdf = open(fn_out, 'rb').read()

        self._try_to_remove_files([fn_in, fn_out])

        return pdf


@shared_task
def get_chemspider_details(cas_number):

    cache_name = 'chemspider-{cas_number}'.format(cas_number=cas_number.replace(' ', '_'))
    d = cache.get(cache_name)
    if d is None:
        d = {"status": "failure"}
        if cas_number:
            try:
                # get chemspider chem id
                url = 'http://www.chemspider.com/Search.asmx/SimpleSearch'
                payload = {'query': cas_number,
                           'token': settings.CHEMSPIDER_TOKEN}
                r = requests.post(url, data=payload)

                id_val = re.search(r'\<int\>(\d+)\</int\>', r.content).group(1)

                # get details
                url = 'http://www.chemspider.com/MassSpecAPI.asmx/GetExtendedCompoundInfo'
                payload = {'CSID': id_val,
                           'token': settings.CHEMSPIDER_TOKEN}
                r = requests.post(url, data=payload)
                xml = ET.fromstring(r.content)
                namespace = '{http://www.chemspider.com/}'
                d['CommonName'] = xml.find('{ns}CommonName'.format(ns=namespace)).text
                d['SMILES'] = xml.find('{ns}SMILES'.format(ns=namespace)).text
                d['MW'] = xml.find('{ns}MolecularWeight'.format(ns=namespace)).text

                # get image
                url = 'http://www.chemspider.com/Search.asmx/GetCompoundThumbnail'
                payload = {'id': id_val,
                           'token': settings.CHEMSPIDER_TOKEN}
                r = requests.post(url, data=payload)
                xml = ET.fromstring(r.content)
                d['image'] = xml.text

                # call it a success if we made it here
                d['status'] = 'success'

                logger.info('setting cache: {cache_name}'.format(cache_name=cache_name))
                cache.set(cache_name, d)
            except Exception as e:
                logger.error(e.message, exc_info=True)

    return d
