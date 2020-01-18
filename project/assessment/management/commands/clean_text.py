# -*- coding: utf-8 -*-

import os
import re

import xlsxwriter
import unicodedata

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.conf import settings


HELP_TEXT = """Remove control characters from a text field"""


class Command(BaseCommand):
    help = HELP_TEXT

    def add_arguments(self, parser):
        parser.add_argument("appname", type=str)
        parser.add_argument("modelname", type=str)
        parser.add_argument("fieldname", type=str)

        parser.add_argument(
            "-t",
            "--test",
            required=False,
            action="store_true",
            help="Create an Excel spreadsheet which shows differences, but don't execute in database",
            dest="test_only",
        )

    def handle(self, *args, **options):
        # check inputs are valid
        if len(options) >= 3:
            model = apps.get_model(options["appname"], options["modelname"])
            qs = model.objects.all()
        else:
            raise CommandError("Requires three arguments: {}".format(options))

        if options.get("test_only"):
            self.test_clean_field(qs, options["fieldname"])
        else:
            self.clean_field(qs, options["fieldname"])

    def clean_field(self, qs, field):
        mods = 0
        for obj in qs:
            txt = getattr(obj, field)
            new_txt = self._cleanup_text(txt)
            if txt != new_txt:
                setattr(obj, field, new_txt)
                try:
                    obj.save()
                    mods += 1
                    self.stdout.write(
                        "Updated {} {}".format(qs.model.__name__, obj.pk),
                        self.style.HTTP_NOT_MODIFIED,
                    )
                except Exception as e:
                    print(e, obj.id)

        self.stdout.write("{} objects were modified".format(mods), self.style.SQL_FIELD)

    def test_clean_field(self, qs, field):
        """
        Print an Excel document showing changes
        """
        # write data rows
        rows = []
        for obj in qs:
            txt = getattr(obj, field)
            new_txt = self._cleanup_text(txt)
            if txt != new_txt:
                rows.append([obj.pk, txt, new_txt])

        if len(rows) > 0:
            # get filename
            fn = os.path.join(settings.PROJECT_PATH, "{}-{}.xlsx".format(qs.model.__name__, field))

            # create WB and WS
            wb = xlsxwriter.Workbook(fn)
            ws = wb.add_worksheet("diff")

            # write header rows
            header_fmt = wb.add_format({"bold": True})
            ws.write(0, 0, "Object ID", header_fmt)
            ws.write(0, 1, "Existing value", header_fmt)
            ws.write(0, 2, "New value", header_fmt)
            ws.freeze_panes(1, 0)

            # write data rows
            for i, row in enumerate(rows):
                ws.write(i + 1, 0, row[0])
                ws.write(i + 1, 1, row[1])
                ws.write(i + 1, 2, row[2])

            wb.close()
            self.stdout.write("Output XLSX: {}".format(fn), self.style.SQL_FIELD)

        self.stdout.write("{} objects would be modified".format(len(rows)), self.style.SQL_FIELD)

    def _cleanup_text(self, s):
        """
        Clean text, which may be extracted via copy-and-paste from a PDF, and
        therefore may have numerous control characters which should be removed.
        """

        # Determine which newlines we want to keep, and which we want to get rid of.
        # If the next character is uppercase, we assume the newline is a paragraph
        # ending; otherwise we get rid of it and replace with a space

        # Remove control characters except line-break
        # http://www.utf8-chartable.de/unicode-utf8-table.pl
        s = re.sub(r"[\u0000-\u0009\u000b-\u001f\u007f-\u009f]", "", s)

        # Cleanup extra newlines-spacing
        # newstr = ""
        # for i, c in enumerate(s):
        #     try:
        #         nextIsUpper = unicodedata.category(s[i+1])=="Lu"
        #     except IndexError:
        #         nextIsUpper = False

        #     if c != "\n" :
        #         newstr += c
        #     elif nextIsUpper:
        #         # extra spacing on paragraphs
        #         newstr += "\n\n"
        #     else:
        #         # convert newline to space if needed
        #         spacing = " "
        #         try:
        #             if s[i-1] == " " or s[i-1] == " ":
        #                 spacing = ""
        #         except IndexError:
        #             spacing = ""

        #         newstr += spacing        # convert newline to space
        # s = newstr

        # Remove trailing spaces
        s = s.strip()

        # Fix quotes
        s = s.replace("‘‘", "“").replace("’’", "”")

        # Remove ALL control characters except our our new-lines above
        return "".join(ch for ch in s if ch == "\n" or unicodedata.category(ch)[0] != "C")
