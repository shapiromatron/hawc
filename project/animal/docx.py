from utils.helper import DOCXReport


class EndpointDOCXReport(DOCXReport):


    def build_summary_table(self):
        cells = [
            {"row":1, "col":0, "val":', '.join(["value"]*20), "rowspan": 2},
            {"row":0, "col":0, "val":"value"},
            {"row":0, "col":1, "val":"value"},
            {"row":0, "col":2, "val":"value"},
            {"row":1, "col":1, "val":"value"},
            {"row":1, "col":2, "val":"value"},
            {"row":2, "col":1, "val":"value"},
            {"row":2, "col":2, "val":', '.join(["value"]*20)},
        ]
        self.build_table(3, 3, cells)

    def apply_context(self):
        doc = self.doc
        d = self.context

        # title
        txt = "Bioassay report: ".format(d['assessment']['name'])
        doc.add_heading(txt, 0)

        # loop through each study
        for study in d['studies']:
            doc.add_heading(study['short_citation'], 1)
            for exp in study['exps']:
                for ag in exp['ags']:
                    self.build_summary_table()

