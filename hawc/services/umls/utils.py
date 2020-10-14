# -*- coding: utf-8 -*-
"""Utils.

@author: scott
"""

from typing import Optional, Set
import spacy

from scispacy.linking import EntityLinker


_cache = {}


def loadUMLSLinker(max_UMLS_Returns, confidence, model="en_core_sci_sm"):
    """Load model."""
    nlp = spacy.load(model)
    linker = EntityLinker(resolve_abbreviations=False, name="umls",
                          max_entities_per_mention=max_UMLS_Returns,
                          threshold=confidence)
    nlp.add_pipe(linker)
    return (linker, nlp)


def flipOnComma(text: str) -> str:
    """Remove commas and reverse string."""
    text_split = text.split(",")
    text_flipped = text_split[::-1]
    text_joined = " ".join(map(str, text_flipped)).strip()
    return text_joined


def umls_to_string(umlsList: list, single_result=True) -> str:
    """Convert umls list of dicts to string."""
    if len(umlsList) == 0:
        return ''
    if not single_result:
        return \
            ' // '.join([i['name'] + ' (' + i['cui'] + ')' for i in umlsList])

    umls_limited = [i for i in umlsList if i['score'] == umlsList[0]['score']]

    return \
        ' // '.join([i['name'] + ' (' + i['cui'] + ')' for i in umls_limited])


def breakIntoSpansAndUMLS(text, nlp, linker,
                          tuiFilter: Optional[Set[str]] = None,
                          confidence=0.5,
                          RequireNonObsoleteDef=False,
                          entity_break=False,
                          cui_limit=5,
                          cache_key=None):
    """Read entities and assign cui."""
    if cache_key is not None:
        if cache_key not in _cache:
            _cache[cache_key] = {}
        elif text in _cache[cache_key]:
            return _cache[cache_key][text]
    doc = nlp(text.strip())
    if entity_break:
        entities = doc.ents
    else:
        entities = [doc[:]]
    umlsList = []
    for entity in entities:
        last_score = 1
        count = 0
        for umls_ent in entity._.umls_ents:
            umls_score = round(umls_ent[1], 4)
            if umls_score < confidence:
                break
            if count >= cui_limit and umls_score < last_score:
                break
            umls_Code = linker.umls.cui_to_entity[umls_ent[0]]
            TUI = umls_Code[3]
            UMLS_Def = umls_Code[4]
            if RequireNonObsoleteDef and \
                    (UMLS_Def is None or "OBSOLETE" in UMLS_Def):
                continue
            if tuiFilter is None or [i for i in TUI if i in tuiFilter]:
                umls_dict = {'name': umls_Code[1],
                             'cui': umls_ent[0],
                             'score': umls_score,
                             'synonyms': umls_Code[2],
                             'tuis': umls_Code[3],
                             'description': umls_Code[4],
                             }
                umlsList.append(umls_dict)
                count += 1
                last_score = umls_score

    if entity_break:
        umls_sorted = sorted(umlsList, key=lambda x: x['score'], reverse=True)
        umls_limited = [i for i in umls_sorted if i['score'] >=
                        umls_sorted[min(cui_limit,
                                        len(umls_sorted))-1]['score']]
        umlsList = umls_limited

    _cache[cache_key][text] = umlsList

    return umlsList
