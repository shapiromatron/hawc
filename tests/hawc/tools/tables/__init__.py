def documents_equal(doc1, doc2):
    # Both documents should have the same number of paragraphs
    equal = len(doc1.paragraphs) == len(doc2.paragraphs)
    if not equal:
        return False
    for i in range(len(doc1.paragraphs)):
        par1 = doc1.paragraphs[i]
        par2 = doc2.paragraphs[i]
        # Both documents should have the same paragraph styles and runs
        equal &= par1.style.name == par2.style.name
        equal &= len(par1.runs) == len(par2.runs)
        if not equal:
            return False
        for j in range(len(par1.runs)):
            run1 = par1.runs[j]
            run2 = par2.runs[j]
            # Both documents should have the same run text and font
            equal &= run1.text == run2.text
            equal &= run1.bold == run2.bold
            equal &= run1.italic == run2.italic
            if not equal:
                return False
    return True
