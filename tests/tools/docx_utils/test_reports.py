import os

from hawc.tools.docx_utils import DOCXReport


class ReporterTest(DOCXReport):
    def create_content(self):
        self.doc.add_heading("Hello {}".format(self.context["name"]), level=1)


def test_reporter():
    root_path = os.path.expanduser("~/Desktop/report.docx")
    report = ReporterTest(None, {"name": "Moto"})
    docx = report.build_report()
    report.save_report(docx, root_path)
