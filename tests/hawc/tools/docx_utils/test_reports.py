from hawc.tools.docx_utils import DOCXReport


class ReporterTest(DOCXReport):
    def create_content(self):
        self.doc.add_heading("Hello {}".format(self.context["name"]), level=1)


def test_reporter():
    report = ReporterTest(None, {"name": "Moto"})
    report.build_report()
