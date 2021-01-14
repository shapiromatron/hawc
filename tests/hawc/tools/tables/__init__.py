def document_compare(doc1, doc2):
    # Both documents should have the same number of paragraphs
    assert len(doc1.paragraphs) == len(doc2.paragraphs)
    for i in range(len(doc1.paragraphs)):
        par1 = doc1.paragraphs[i]
        par2 = doc2.paragraphs[i]
        # Both documents should have the same paragraph styles and runs
        assert par1.style.name == par2.style.name
        assert len(par1.runs) == len(par2.runs)
        for j in range(len(par1.runs)):
            run1 = par1.runs[j]
            run2 = par2.runs[j]
            # Both documents should have the same run text and font
            assert run1.text == run2.text
            assert run1.bold == run2.bold
            assert run1.italic == run2.italic
