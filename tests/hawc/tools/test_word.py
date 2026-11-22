from docx import Document

from hawc.tools.word import add_url_hyperlink, write_setting_p


def test_write_setting_p():
    doc = Document()
    write_setting_p(doc, "Title: ", "value")
    runs = doc.paragraphs[0].runs
    assert [(r.text, r.bold) for r in runs] == [("Title: ", True), ("value", None)]


def test_add_url_hyperlink():
    doc = Document()
    paragraph = doc.add_paragraph()
    add_url_hyperlink(paragraph, "https://example.com", "link")
    assert "https://example.com" in [rel.target_ref for rel in doc.part.rels.values()]
    assert paragraph.runs[0].font.underline is True
    assert "link" in paragraph._p.xml
