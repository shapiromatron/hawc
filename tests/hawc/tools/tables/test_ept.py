from pathlib import Path

from docx import Document

from hawc.tools.tables.ept import EvidenceProfileTable

from . import documents_equal

DATA_PATH = Path(__file__).parent.absolute() / "data"


class TestEvidenceProfileTable:
    def test_docx(self):
        document = Document()
        table = EvidenceProfileTable.build_default()
        document = table.to_docx()
        saved_document = Document(DATA_PATH / "ept_report.docx")

        assert documents_equal(document, saved_document)
