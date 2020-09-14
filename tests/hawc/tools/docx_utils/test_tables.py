from hawc.tools.docx_utils import DOCXReport, TableMaker


class TableTester(DOCXReport):
    def create_content(self):
        tbl = TableMaker([2, 2, 2], numHeaders=1, firstRowCaption=False)

        # headers
        tbl.new_th(0, 0, "A")
        tbl.new_th(0, 1, "B")
        tbl.new_th(0, 2, "C")

        # texts and runs
        tbl.new_td_txt(1, 0, "D")
        tbl.new_td_run(
            1,
            1,
            [
                tbl.new_run("Normal"),
                tbl.new_run("Bold", b=True),
                tbl.new_run("Italic", i=True),
                tbl.new_run("NoNewline", newline=False),
                tbl.new_run("\tCustomStyle", style="Strong"),
            ],
            colspan=2,
            rowspan=2,
        )
        tbl.new_td_txt(2, 0, "E")

        # fills and alignments
        tbl.new_td_txt(3, 0, "F", shade="#57CF52")
        tbl.new_td_txt(3, 1, "G")
        tbl.new_td_txt(3, 2, "Vertical", vertical=True, height=1)

        # render
        tbl.render(self.doc)


def test_table():
    report = TableTester(None, {"name": "Moto"})
    report.build_report()
