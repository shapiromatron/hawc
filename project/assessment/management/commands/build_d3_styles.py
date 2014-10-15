import os
import re

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


HELP_TEXT = """Assemble all CSS styles used in d3 visualizations and create a
new CSS file which can be inserted into static SVG files containing all the
style information from external-style sheets."""


class Command(BaseCommand):
    args = ''
    help = HELP_TEXT

    def handle(self, *args, **options):
        if len(args)>0:
            raise CommandError("No inputs are taken for this command.")

        static_path = os.path.abspath(os.path.join(settings.PROJECT_PATH, 'static'))

        def remove_spacing(txt, character):
            txt = re.sub(character + ' ', character, txt)
            return re.sub(' ' + character, character, txt)

        # Only using D3.css as adding other style-sheets with non SVG styles can
        # potentially break the Inkscape SVG processor.
        files = ('css/d3.css', )

        txt = ''
        for fn in files:
            with open(os.path.join(static_path, fn), 'r') as f:
                txt = txt + f.read() + ' '
        txt = re.sub(r'\/\*[^(\*\/)]+\*\/', ' ', txt)
        txt = re.sub(r'\n', ' ', txt)
        txt = re.sub(r' >', ' ', txt)  # this style-type can break illustrator
        txt = re.sub(r'[ ]+', ' ', txt)
        txt = remove_spacing(txt, ":")
        txt = remove_spacing(txt, "{")
        txt = remove_spacing(txt, "}")
        txt = remove_spacing(txt, ";")
        txt = re.sub(r'}', r'}\n', txt)

        with open(os.path.join(static_path, 'css/hawc_d3_aggregated.css'), 'w+') as f:
            f.write(txt)
