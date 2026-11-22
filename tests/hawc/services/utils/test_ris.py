import io
import logging
from pathlib import Path

import pytest
from rispy.parser import ParseError

from hawc.services.utils import ris
from hawc.services.utils.ris import ReferenceParser, RisImporter

DATA_ROOT = Path(__file__).parent / "data"


def test_parsing():
    fn = DATA_ROOT / "sample_ris.txt"

    # assert successful import of all references
    importer = RisImporter(str(fn))
    refs = importer.references
    assert len(refs) == 10

    # test journal-style import
    test = {
        "accession_number": "2003114678",
        "abstract": "When chlorine is introduced into public drinking water for disinfection, it can react with organic compounds in surface waters to form toxic by-products such as 3-chloro-4-(dichloromethyl)-5-hydroxy-2[5H]-furanone (MX). We investigated the effect of exposure to MX on cytochrome P450 2E1 (CYP2E1)-like activity and total glutathione (GSH) in the liver of the small fish model, medaka (Oryzias latipes). The multi-site carcinogen methylazoxymethanol acetate (MAMAc) was the positive control compound. Both medaka liver microsome preparations and S-9 fractions catalyzed the hydroxylation of p-nitrophenol (PNP), suggesting CYP2E1-like activity in the medaka. Male medaka exposed for 96 h to the CYP2E1 inducers ethanol and acetone under fasted conditions showed significant increases in PNP-hydroxylation activity. Furthermore, total reduced hepatic GSH was reduced in fish fasted for 96 h, indicating that normal feeding is a factor in maintaining xenobiotic defenses. Exposure to MX and MAMAc induced significant increases in hepatic CYP2E1-like activity, however MX exposure did not alter hepatic GSH levels. These data strengthen the role of the medaka as a suitable species for examining cytochrome P450 and GSH detoxification processes and the role these systems play in chemical carcinogenesis. \u00a9 2003 Elsevier Science Inc. All rights reserved.",
        "citation": "Comparative Biochemistry and Physiology - C Toxicology and Pharmacology 2003; 134 (3):353-364",
        "authors_short": "Geter DR et al.",
        "authors": ["Geter DR", "Fournie JW", "Brouwer MH", "DeAngelo AB", "Hawkins WE"],
        "year": 2003,
        "id": 288,
        "doi": "10.1016/S1532-0456(03)00003-6",
        "title": "p-Nitrophenol and glutathione response in medaka (Oryzias latipes) exposed to MX, a drinking water carcinogen",
        "reference_type": "JOUR",
        "accession_db": "Embase",
        "PMID": 12643982,
    }
    ref = refs[0]
    ref.pop("json")
    assert ref == test

    # test chapter-style import
    test = {
        "accession_number": None,
        "abstract": "",
        "citation": "Applications of Toxicogenomics in Safety Evaluation and Risk Assessment. 2011. Pages 41-64. 9780470449820 (ISBN)",
        "authors_short": "Boverhof DR et al.",
        "authors": ["Boverhof DR", "Geter DR", "Gollapudi BB", "Hollnagel H"],
        "year": 2011,
        "id": 11,
        "doi": "10.1002/9781118001042.ch3",
        "title": "Practical Considerations for the Application of Toxicogenomics to Risk Assessment: Early Experience, Current Drivers, and a Path Forward",
        "reference_type": "CHAP",
        "accession_db": "Scopus",
        "PMID": None,
    }
    ref = refs[5]
    ref.pop("json")
    assert ref == test

    # test conference-style import
    test = {
        "accession_number": None,
        "citation": "2013 International Conference on Human Health and Medical Engineering, HHME 2013",
        "authors_short": "",
        "authors": [],
        "year": 2014,
        "id": 823,
        "doi": None,
        "title": "2013 International Conference on Human Health and Medical Engineering, HHME 2013",
        "reference_type": "CONF",
        "accession_db": "Scopus",
        "PMID": None,
    }
    ref = refs[9]
    ref.pop("json")
    ref.pop("abstract")
    assert ref == test

    # test unicode-authors
    test = "Radomska-Leśniewska DM and Skopiński P"
    assert test == refs[8]["authors_short"]

    # test import with unknown tags
    ref = refs[4]
    ref_json = ref.pop("json")
    assert ref_json["unknown_tag"] == {"JP": ["CRISPR"], "DC": ["Direct Current"]}


def test_accession_nuber():
    fn = DATA_ROOT / "accession-numbers.txt"
    importer = RisImporter(str(fn))
    refs = importer.references

    # accession numbers
    ans = {ref["id"]: ref["accession_number"] for ref in refs}
    assert ans == {1: "1234", 2: "abc", 3: "123", 4: None, 5: None}


class TestRisImporter:
    def test_file_object(self):
        f = io.StringIO("TY  - JOUR\nID  - 1\nER  - \n")
        importer = RisImporter(f)
        assert importer.raw_references == [{"type_of_reference": "JOUR", "id": "1"}]
        assert len(importer.references) == 1
        assert f.closed

    def test_file_readable(self):
        f = io.StringIO("TY  - JOUR\nID  - 1\nER  - \n")
        assert RisImporter.file_readable(f) is True
        assert f.tell() == 0

    def test_file_not_readable(self, monkeypatch, caplog):
        def raise_error(*args, **kwargs):
            raise ParseError("bad file")

        monkeypatch.setattr(ris.rispy, "load", raise_error)
        caplog.set_level(logging.WARNING, logger=ris.logger.name)
        assert RisImporter.file_readable(io.StringIO("")) is False
        assert "bad file" in caplog.text


class TestReferenceParser:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [(None, None), ("", None), (" ", None), ("2020", 2020)],
    )
    def test_get_year(self, value, expected):
        assert ReferenceParser({}).get_year(value) == expected

    def test_get_year_invalid(self):
        with pytest.raises(ValueError, match="Invalid year: abc"):
            ReferenceParser({}).get_year("abc")

    def test_get_doi(self):
        assert ReferenceParser({"doi": "10.1/abc"}).get_doi(None) == "10.1/abc"
        with pytest.raises(ValueError, match="DOI too long"):
            ReferenceParser({"doi": "1" * 257}).get_doi(None)

    def test_get_id(self):
        assert ReferenceParser({}).get_id("123") == 123

    @pytest.mark.parametrize("value", [None, "abc"])
    def test_get_id_invalid(self, value):
        with pytest.raises(ValueError, match=ReferenceParser.ID_MISSING):
            ReferenceParser({}).get_id(value)

    @pytest.mark.parametrize(
        ("content", "expected"),
        [
            ({"pubmed_id": 123}, 123),
            ({"pubmed_id": "PMID: 456 (url/789)"}, 456),
            ({"pubmed_id": "none"}, None),
            ({"name_of_database": "NLM", "accession_number": "789"}, 789),
            ({"name_of_database": "NLM", "accession_number": "abc"}, None),
            ({"name_of_database": "Embase", "accession_number": "789"}, None),
            ({}, None),
        ],
    )
    def test_get_pmid(self, content, expected):
        assert ReferenceParser(content)._get_pmid() == expected

    @pytest.mark.parametrize(
        ("number", "expected"),
        [
            (" 123 ", "123"),
            ("https://foo.com/?eid=2-s2.0-123&partnerID=1", "2-s2.0-123"),
            ("eid=", "eid="),
            ("null", None),
            (None, None),
        ],
    )
    def test_get_accession_number(self, number, expected):
        content = {} if number is None else {"accession_number": number}
        assert ReferenceParser(content)._get_accession_number() == expected

    @pytest.mark.parametrize(
        ("content", "expected"),
        [
            (
                {
                    "type_of_reference": "JOUR",
                    "secondary_title": "J Tox",
                    "year": "2020",
                    "volume": "1",
                    "note": "2",
                    "start_page": "3",
                },
                "J Tox 2020; 1 (2):3",
            ),
            ({"type_of_reference": "JFULL", "year": "2020"}, " 2020"),
            (
                {
                    "type_of_reference": "BOOK",
                    "secondary_title": "Book",
                    "year": "2020",
                    "start_page": "3",
                    "issn": "1234",
                },
                "Book. 2020. Pages 3. 1234",
            ),
            ({"type_of_reference": "CHAP"}, ""),
            ({"type_of_reference": "SER", "alternate_title1": "Series"}, "Series"),
            ({"type_of_reference": "SER"}, ""),
            ({"type_of_reference": "CONF", "short_title": "Conf"}, "Conf"),
            ({"type_of_reference": "CONF"}, ""),
        ],
    )
    def test_get_citation(self, content, expected):
        assert ReferenceParser(content)._get_citation() == expected

    def test_get_citation_unknown_type(self, caplog):
        caplog.set_level(logging.WARNING, logger=ris.logger.name)
        parser = ReferenceParser({"type_of_reference": "XXXX", "id": 5})
        assert parser._get_citation() == ReferenceParser.PLACEHOLDER_TEXT
        assert 'Unknown type: "XXXX", id="5"' in caplog.text

    def test_clean_authors(self):
        parser = ReferenceParser(
            {"authors": ["Smith, J"], "first_authors": ["Doe, A"], "title": "ignored"}
        )
        parser._clean_authors()
        assert parser._authors == ["Smith J", "Doe A"]

    def test_clean_authors_none(self):
        parser = ReferenceParser({})
        parser._clean_authors()
        assert parser._authors == []

    @pytest.mark.parametrize(
        ("content", "expected"),
        [
            ({}, ""),
            ({"authors": ["Smith, J"]}, "Smith J"),
            ({"authors": ["Smith, J", "Doe, A"]}, "Smith J and Doe A"),
            ({"authors": ["Smith, J", "Doe, A", "Roe, B"]}, "Smith J, Doe A, and Roe B"),
            (
                {"authors": ["Smith, J"], "first_authors": ["Doe, A", "Roe, B", "Poe, C"]},
                "Smith J et al.",
            ),
        ],
    )
    def test_get_authors_short(self, content, expected):
        assert ReferenceParser(content)._get_authors_short() == expected

    def test_format(self):
        content = {
            "type_of_reference": "SER",
            "alternate_title1": "Series",
            "authors": ["Smith, J"],
            "id": "7",
            "year": "2020",
            "doi": "10.1/abc",
            "pubmed_id": 12,
        }
        parser = ReferenceParser(content)
        formatted = parser.format()
        assert formatted is parser.format()
        assert formatted == {
            "authors_short": "Smith J",
            "authors": ["Smith J"],
            "title": ReferenceParser.PLACEHOLDER_TEXT,
            "year": 2020,
            "citation": "Series",
            "abstract": "",
            "PMID": 12,
            "doi": "10.1/abc",
            "accession_number": None,
            "accession_db": None,
            "reference_type": "SER",
            "id": 7,
            "json": content,
        }
