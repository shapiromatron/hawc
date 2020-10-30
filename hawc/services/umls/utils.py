# -*- coding: utf-8 -*-
"""Utils.

@author: scott
"""

import spacy
from scispacy.linking import EntityLinker
from rapidfuzz import fuzz
import numpy as np


_cache = {}


def loadUMLSLinker(max_UMLS_Returns=999, confidence=0.5,
                   model="en_core_sci_sm"):
    """Load model."""
    nlp = spacy.load(model)
    linker = EntityLinker(resolve_abbreviations=False, name="umls",
                          max_entities_per_mention=max_UMLS_Returns,
                          threshold=confidence)
    nlp.add_pipe(linker)
    return (linker, nlp)


def loadDocs(series, nlp):
    """Run nlp on text."""
    series_list = series.drop_duplicates().apply(transformComma, entity=True)
    text_list = set([j.strip() for i in series_list for j in i if len(j) > 2])
    docs_dict = {text: nlp(text) for text in text_list}
    return docs_dict


def transformComma(text: str, entity: bool) -> list:
    """Remove commas and reverse string."""
    if text.endswith('.'):
        return [text]
    text_split = [str(i).strip() for i in text.split(",")]
    text_flipped = [str(i).strip() for i in text_split[::-1]]
    comma_removed = " ".join(text_split)
    comma_reversed = " ".join(text_flipped)
    comb = [comma_reversed, comma_removed]
    comb.append(text)
    if entity:
        comb += text_split[:1]
    return comb


def umls_filter(x, string=False, max_results=5, strict=True) -> str:
    """Convert umls list of dicts to string."""
    text = x.iloc[0]
    umlsList = x.iloc[1]

    for i in range(2, len(x.index)):
        for k in x.iloc[i]:
            if k['cui'] not in [j['cui'] for j in umlsList]:
                umlsList.append(k)

    if len(umlsList) == 0:
        return '' if string else []

    text_split = [str(i).strip().lower() for i in text.split(",")
                  if len(i.strip()) > 2]
    text_transformed = [i.lower() for i in transformComma(text, False)]
    tiers = [[] for i in range(len(text_split) + 2)]

    for val in umlsList:
        syns = [i.lower() for i in val['synonyms']] + [val['name'].lower()]
        score_d = {j:
                   np.median([fuzz.token_sort_ratio(j, i) for i in syns])/100
                   for j in set(text_transformed + text_split)}
        added = False

        for i in text_transformed:
            if i in syns:
                tiers[0].append((val, score_d[i]))
                added = True
                break
        if added:
            continue

        for n, i in enumerate(text_split):
            if i in syns:
                tiers[n+1].append((val, score_d[i]/(n+1)/len(text_split)))
                added = True
                break
        if added:
            continue

        comb_score = np.median(
            [score_d[i]/(n+1)/len(text_split)
             for n, i in enumerate(text_split)])

        tiers[-1].append((val, comb_score))

    results_list = []
    for n, i in enumerate(tiers):
        if strict and n == len(tiers)-1 and len(results_list) > 0:
            break
        if len(i) == 0:
            continue
        results_list += sorted(i, key=lambda x: x[1], reverse=True)
        if n == 0:
            break
    results_list2 = sorted(results_list, key=lambda x: x[1], reverse=True)
    if results_list != results_list2:
        pass

    results_list = results_list[:max_results]

    if string:
        return ' // '.join(
            [i[0]['name'] + ' (' + i[0]['cui'] + '; ' +
             ', '.join(i[0]['tuis']) + '; ' + str(i[1]) + ')'
             for i in results_list])
    else:
        return results_list


def breakIntoSpansAndUMLS(text, docs_dict, linker,
                          tuiFilter=None,
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
    confidence = 0 if confidence is None else confidence
    cui_limit = 999 if cui_limit is None else cui_limit
    docs = [docs_dict[text_transformed.strip()]
            for text_transformed in transformComma(text, entity_break)
            if len(text_transformed) > 2]
    if entity_break:
        entities = [i for doc in docs for i in list(doc.ents)]
    else:
        entities = [doc[:] for doc in docs]
    save_cui = {}
    for entity in entities:
        last_score = 1
        count = 0
        for umls_ent in entity._.umls_ents:
            umls_score = round(umls_ent[1], 4)
            if umls_ent[0] in save_cui:
                if save_cui[umls_ent[0]]['score'] < umls_score:
                    save_cui[umls_ent[0]]['score'] = umls_score
                continue
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
                count += 1
                last_score = umls_score
                save_cui[umls_ent[0]] = umls_dict
    umlsList = [val for key, val in save_cui.items()]

    umls_sorted = sorted(umlsList, key=lambda x: x['score'], reverse=True)
    umls_limited = [i for i in umls_sorted if i['score'] >=
                    umls_sorted[min(cui_limit,
                                    len(umls_sorted))-1]['score']]
    umlsList = umls_limited

    _cache[cache_key][text] = umlsList

    return umlsList
