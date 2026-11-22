from pathlib import Path

import pytest
from docx import Document

from hawc.tools.tables.ept import (
    CertainFactorsCell,
    EvidenceCell,
    EvidenceGroup,
    EvidenceProfileTable,
    EvidenceRow,
    Factor,
    FactorsCell,
    FactorType,
    JudgementCell,
    JudgementChoices,
    MechanisticEvidenceCell,
    MechanisticGroup,
    MechanisticJudgementCell,
    MechanisticRow,
    MechanisticSummaryCell,
    SummaryCell,
    SummaryJudgementCell,
    SummaryJudgementChoices,
    UncertainFactorsCell,
)
from hawc.tools.tables.parser import QuillParser

from . import block_text, documents_equal

FILE_PATH = Path(__file__).parent.absolute() / "data" / "ept_report.docx"


def feed(cell) -> list[str]:
    """Render a cell into a blank document and return its paragraph texts."""
    body = Document()._body
    parser = QuillParser()
    # the parser expects a prior paragraph for leading text; in tables it is shared across cells
    parser.feed("<p></p>", body)
    cell.to_docx(parser, body)
    return block_text(body)[1:]


def judgement_kwargs(**kwargs):
    return {"judgement": JudgementChoices.Indeterminate, "description": "<p>d</p>", **kwargs}


def summary_kwargs(**kwargs):
    empty = "<p></p>"
    return {
        "judgement": SummaryJudgementChoices.Inadequate,
        "description": empty,
        "human_relevance": empty,
        "cross_stream_coherence": empty,
        "susceptibility": empty,
        "plausibility": empty,
        "other": empty,
        "hide_content": False,
        **kwargs,
    }


def evidence_row(n: int = 1) -> dict:
    return {
        "evidence": {"description": f"<p>evidence {n}</p>"},
        "summary": {"findings": f"<p>summary {n}</p>"},
        "certain_factors": {"text": "<p></p>", "factors": []},
        "uncertain_factors": {"text": "<p></p>", "factors": []},
        "judgement": judgement_kwargs(description=f"<p>judgement {n}</p>"),
    }


def mechanistic_row(n: int = 1) -> dict:
    return {
        "evidence": {"description": f"<p>evidence {n}</p>"},
        "summary": {"findings": f"<p>summary {n}</p>"},
        "judgement": {"description": f"<p>judgement {n}</p>"},
    }


def group_kwargs(**kwargs):
    return {
        "title": "Title",
        "rows": [],
        "merge_judgement": False,
        "hide_content": False,
        "no_content_text": "None",
        **kwargs,
    }


class TestSummaryJudgementCell:
    def test_judgement_html(self):
        def html(**kwargs):
            return SummaryJudgementCell(**summary_kwargs(**kwargs)).judgement_html()

        assert html(judgement=SummaryJudgementChoices.NoJudgement) == ""
        assert html(
            judgement=SummaryJudgementChoices.Custom,
            custom_judgement_icon="*",
            custom_judgement_label="Custom",
        ) == ("<p>*</p><p><em>Custom</em></p>")
        assert html() == "<p>⊙⊙⊙</p><p><em>Evidence inadequate</em></p>"

    def test_to_docx(self):
        full = summary_kwargs(
            description="<p>desc</p>",
            human_relevance="<p>hr</p>",
            cross_stream_coherence="<p>csc</p>",
            susceptibility="<p>sus</p>",
            plausibility="<p>plaus</p>",
            other="<p>other</p>",
        )
        paragraphs = feed(SummaryJudgementCell(**full))
        assert paragraphs[:2] == ["⊙⊙⊙", "Evidence inadequate"]
        assert [p for p in paragraphs if p] == [
            "⊙⊙⊙",
            "Evidence inadequate",
            "desc",
            "Human relevance of findings in animals:",
            "hr",
            "Cross-stream coherence:",
            "csc",
            "Potential susceptibility:",
            "sus",
            "Biological plausibility:",
            "plaus",
            "Other critical inferences (e.g., ADME, or other supplemental information):",
            "other",
        ]

    def test_to_docx_no_judgement(self):
        cell = SummaryJudgementCell(
            **summary_kwargs(judgement=SummaryJudgementChoices.NoJudgement, description="<p>d</p>")
        )
        assert [p for p in feed(cell) if p] == ["d"]


@pytest.mark.parametrize(
    ("cell", "expected"),
    [
        (EvidenceCell(description="<p>a</p>"), ["a"]),
        (SummaryCell(findings="<p>b</p>"), ["b"]),
        (MechanisticEvidenceCell(description="<p>c</p>"), ["c"]),
        (MechanisticSummaryCell(findings="<p>d</p>"), ["d"]),
        (MechanisticJudgementCell(description="<p>e</p>"), ["e"]),
    ],
)
def test_simple_cells_to_docx(cell, expected):
    assert feed(cell) == expected


class TestFactor:
    @pytest.mark.parametrize(
        ("key", "short_description", "expected"),
        [
            (FactorType.UpConsistency, "<p>text</p>", "<em>Consistency</em> - text"),
            (FactorType.UpConsistency, "<p></p>", "<em>Consistency</em>"),
            (FactorType.UpOther, "<p>other</p>", "other"),
        ],
    )
    def test_to_html(self, key, short_description, expected):
        factor = Factor(key=key, short_description=short_description, long_description="")
        assert factor.to_html() == expected


class TestFactorsCell:
    def test_factor_types(self):
        cell = FactorsCell(factors=[], text="")
        with pytest.raises(NotImplementedError):
            cell.factor_types  # noqa: B018

    @pytest.mark.parametrize("cls", [CertainFactorsCell, UncertainFactorsCell])
    def test_to_docx(self, cls):
        up, down = FactorType.UpConsistency, FactorType.DownConsistency
        factors = [
            Factor(key=k, short_description="<p></p>", long_description="")
            for k in (down, up, FactorType.NoFactors)
        ]
        cell = cls(factors=factors, text="<p>footer</p>")
        expected = "Consistency" if cls is CertainFactorsCell else "Unexplained inconsistency"
        assert feed(cell) == ["No factors noted", expected, "footer"]
        assert [f.key for f in cell.sorted_factors] == [
            FactorType.NoFactors,
            up if cls is CertainFactorsCell else down,
        ]

    def test_to_docx_no_factors(self):
        assert feed(CertainFactorsCell(factors=[], text="<p>footer</p>")) == ["footer"]


class TestJudgementCell:
    def test_judgement_html(self):
        def html(**kwargs):
            return JudgementCell(**judgement_kwargs(**kwargs)).judgement_html()

        assert html(judgement=JudgementChoices.NoJudgement) == ""
        assert html(
            judgement=JudgementChoices.Custom,
            custom_judgement_icon="*",
            custom_judgement_label="Custom",
        ) == ("<p>*</p><p><em>Custom</em></p>")
        assert html() == "<p>⊙⊙⊙</p><p><em>Indeterminate</em></p>"

    def test_to_docx(self):
        assert feed(JudgementCell(**judgement_kwargs())) == ["⊙⊙⊙", "Indeterminate", "d"]
        cell = JudgementCell(**judgement_kwargs(judgement=JudgementChoices.NoJudgement))
        assert feed(cell) == ["d"]


class TestEvidenceRow:
    def test_cells(self):
        row = EvidenceRow(**evidence_row())
        assert [c.column for c in row.cells] == [0, 1, 2, 3, 4]


class TestMechanisticRow:
    def test_cells(self):
        row = MechanisticRow(**mechanistic_row())
        assert [c.column for c in row.cells] == [0, 1, 4]


class TestEvidenceGroup:
    def test_no_rows(self):
        group = EvidenceGroup(**group_kwargs())
        assert [(c.row, c.col_span) for c in group.cells] == [(0, 5), (1, 5)]

    def test_merge_judgement(self):
        rows = [evidence_row(1), evidence_row(2)]
        group = EvidenceGroup(**group_kwargs(rows=rows, merge_judgement=True))
        assert len(group.cells) == 1 + 5 + 4
        assert group.cells[5].row_span == 2

    def test_no_merge_judgement(self):
        rows = [evidence_row(1), evidence_row(2)]
        group = EvidenceGroup(**group_kwargs(rows=rows))
        assert len(group.cells) == 1 + 5 + 5
        assert group.rows == 3


class TestMechanisticGroup:
    kwargs = {"col_header_1": "Header"}

    def test_column_headers(self):
        group = MechanisticGroup(**group_kwargs(**self.kwargs))
        assert [c.col_span for c in group.column_headers] == [1, 3, 1]

    def test_no_rows(self):
        group = MechanisticGroup(**group_kwargs(**self.kwargs))
        assert [(c.row, c.col_span) for c in group.cells] == [
            (0, 5),
            (1, 1),
            (1, 3),
            (1, 1),
            (2, 5),
        ]

    def test_merge_judgement(self):
        rows = [mechanistic_row(1), mechanistic_row(2)]
        group = MechanisticGroup(**group_kwargs(rows=rows, merge_judgement=True, **self.kwargs))
        assert len(group.cells) == 1 + 3 + 3 + 2
        assert group.rows == 4

    def test_no_merge_judgement(self):
        rows = [mechanistic_row(1), mechanistic_row(2)]
        group = MechanisticGroup(**group_kwargs(rows=rows, **self.kwargs))
        assert len(group.cells) == 1 + 3 + 3 + 3


class TestEvidenceProfileTable:
    def test_docx(self, rewrite_data_files: bool):
        document = Document()
        table = EvidenceProfileTable.build_default()
        document = table.to_docx()
        if rewrite_data_files:
            document.save(FILE_PATH)
        saved_document = Document(FILE_PATH)

        assert documents_equal(document, saved_document)

    @pytest.mark.parametrize(
        ("hide", "n_cells"),
        [
            # (human, animal, mechanistic, summary): visible content determines the cell count
            ((False, False, False, False), None),
            ((True, True, True, False), 2),
            ((True, True, True, True), 0),
            ((True, True, False, True), None),
            ((False, True, True, True), None),
        ],
    )
    def test_set_cells(self, hide, n_cells):
        props = EvidenceProfileTable.get_default_props()
        for key, hidden in zip(
            ["exposed_human", "animal", "mechanistic", "summary_judgement"], hide, strict=True
        ):
            props[key]["hide_content"] = hidden
        table = EvidenceProfileTable.model_validate(props)
        if n_cells is not None:
            assert len(table.cells) == n_cells
        else:
            assert len(table.cells) > 0
