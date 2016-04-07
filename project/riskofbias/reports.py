from django.utils.html import strip_tags

from docxUtils.tables import TableMaker

from utils.helper import HAWCDOCXReport

from models import RiskOfBias


class RoBDOCXReport(HAWCDOCXReport):

    def create_content(self):
        d = self.context

        self.setMargins(left=0.5, right=0.5)

        txt = "Risk-of-bias report: {0}".format(d['assessment']['name'])
        self.doc.add_heading(txt, 1)

        for study in d['studies']:
            self.doc.add_heading(study['short_citation'], 2)
            if len(study["qualities"]) > 0:
                self.build_ROB_table(study)
                self.doc.add_paragraph()
                self.build_ROB_legend()
                self.doc.add_page_break()
            else:
                self.doc.add_paragraph("No risk-of-bias details available for this study.")

    def getTableCaptionRuns(self, study):
        return [
            TableMaker.new_run(u'{0}: '.format(study["short_citation"]), b=True, newline=False),
            TableMaker.new_run(study["full_citation"], newline=False)
        ]

    def build_ROB_table(self, study):
        widths = [2.8, 0.7, 4.0]
        tbl = TableMaker(widths, numHeaders=2, firstRowCaption=True, tblStyle="ntpTbl")

        # add caption
        tbl.new_td_run(0, 0, self.getTableCaptionRuns(study), colspan=3)

        # add headers
        cells = ['Risk of Bias', 'Rating', 'Rating rationale']
        for i, cell in enumerate(cells):
            tbl.new_th(1, i, cell)

        # add body
        row = 2
        for d in study["qualities"]:
            tbl.new_td_txt(row, 0, d["metric"]["metric"])
            tbl.new_td_txt(row, 1, d["score_symbol"], shade=d["score_shade"])
            tbl.new_td_txt(row, 2, strip_tags(d["notes"]))
            row += 1

        return tbl.render(self.doc)

    def build_ROB_legend(self):
        widths = [1.5, 1.0, 0.4, 1.0, 0.4, 1.0, 0.4, 0.4, 1.0, 0.4]
        tbl = TableMaker(widths, numHeaders=0, firstRowCaption=False, tblStyle="ntpTbl")
        cells = [
           {"runs": [TableMaker.new_run("Risk of bias key:", b=True, newline=False)]},
           {"text": "Definitely Low"},
           {"text": "++", "shade": RiskOfBias.SCORE_SHADES[4]},
           {"text": "Probably Low"},
           {"text": "+", "shade": RiskOfBias.SCORE_SHADES[3]},
           {"text": "Probably High"},
           {"text": "-", "shade": RiskOfBias.SCORE_SHADES[2]},
           {"text": "NR", "shade": RiskOfBias.SCORE_SHADES[0]},
           {"text": "Definitely High"},
           {"text": "--", "shade": RiskOfBias.SCORE_SHADES[1]},
        ]
        for i, cell in enumerate(cells):
            if "runs" in cell:
                tbl.new_td_run(0, i, cell["runs"], shade=cell.get("shade"))
            else:
                tbl.new_td_txt(0, i, cell["text"], shade=cell.get("shade"))

        return tbl.render(self.doc)
