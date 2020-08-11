import json
from typing import Dict, Optional, Set

import requests
import spacy
from scispacy.umls_linking import UmlsEntityLinker

from .auth import Authentication


def UMLS_RestLookup(string, apikey):
    umls_dictionary = dict()
    while True:
        if string in umls_dictionary:
            jsonData = umls_dictionary.get(string)
        else:
            uri = "https://uts-ws.nlm.nih.gov"
            content_endpoint = "/rest/search/current"
            pageNumber = 0
            AuthClient = Authentication(apikey)
            tgt = AuthClient.gettgt()
            ticket = AuthClient.getst(tgt)
            pageNumber += 1
            query = {"string": string, "ticket": ticket, "pageNumber": pageNumber}
            query["inputType"] = "atom"
            query["includeObsolete"] = "false"
            query["includeSuppressible"] = "false"
            query["searchType"] = "exact"
            query["pageNumber"] = 1
            query["pageSize"] = 3
            r = requests.get(uri + content_endpoint, params=query)
            r.encoding = "utf-8"
            items = json.loads(r.text)
            jsonData = items["result"]
            umls_dictionary[string] = jsonData
        return jsonData


def loadUMLSLinker(max_UMLS_Returns, confidence, model="en_core_sci_sm"):
    nlp = spacy.load(model)
    linker = UmlsEntityLinker(
        resolve_abbreviations=False, max_entities_per_mention=max_UMLS_Returns, threshold=confidence
    )
    nlp.add_pipe(linker)
    return (linker, nlp)


def flipOnComma(text: str) -> str:
    text_split = text.split(",")
    text_flipped = text_split[::-1]
    text_joined = " ".join(map(str, text_flipped)).strip()
    return text_joined


def breakIntoEntities(text, nlp):
    doc = nlp(text)
    entities = doc.ents
    return entities


def breakIntoSpansAndUMLS(
    text, nlp, linker, tuiFilter: Optional[Set[str]] = None, RequireNonObsoleteDef=False
):
    doc = nlp(text.strip())
    entity = doc[:]
    umlsList = ""
    count = 0
    for umls_ent in entity._.umls_ents:
        umls_Code = linker.umls.cui_to_entity[umls_ent[0]]
        TUI = umls_Code[3]
        UMLS_Def = umls_Code[4]
        if RequireNonObsoleteDef is False:
            if tuiFilter is None:
                umls_Score = umls_ent[1]
                umlsList += str(umls_Code) + " SCORE: " + str(umls_Score) + "\n"
                count += 1
            elif TUI in tuiFilter:
                umls_Score = umls_ent[1]
                umlsList += str(umls_Code) + " SCORE: " + str(umls_Score) + "\n"
                count += 1
        elif RequireNonObsoleteDef is True:
            if UMLS_Def is None or "OBSOLETE" in UMLS_Def:
                pass
            elif tuiFilter is None and UMLS_Def is not None and "OBSOLETE" not in UMLS_Def:
                umls_Score = umls_ent[1]
                umlsList += str(umls_Code) + " SCORE: " + str(umls_Score) + "\n"
                count += 1
            elif TUI in tuiFilter and UMLS_Def is not None and "OBSOLETE" not in UMLS_Def:
                umls_Score = umls_ent[1]
                umlsList += str(umls_Code) + " SCORE: " + str(umls_Score) + "\n"
                count += 1
    return (umlsList, count)


def breakIntoEntitiesAndUMLS(
    text, nlp, linker, tuiFilter: Optional[Set[str]] = None, RequireNonObsoleteDef=False
):
    umlsList = ""
    doc = nlp(text)
    entities = doc.ents
    count = 0
    for entity in entities:
        for umls_ent in entity._.umls_ents:
            umls_Code = linker.umls.cui_to_entity[umls_ent[0]]
            TUI = umls_Code[3]
            UMLS_Def = umls_Code[4]
            if RequireNonObsoleteDef is False:
                if tuiFilter is None:
                    umls_Score = umls_ent[1]
                    umlsList += str(umls_Code) + " SCORE: " + str(umls_Score) + "\n"
                    count += 1
                elif TUI in tuiFilter:
                    umls_Score = umls_ent[1]
                    umlsList += str(umls_Code) + " SCORE: " + str(umls_Score) + "\n"
                    count += 1
            elif RequireNonObsoleteDef is True:
                if UMLS_Def is None or "OBSOLETE" in UMLS_Def:
                    pass
                elif tuiFilter is None and UMLS_Def is not None and "OBSOLETE" not in UMLS_Def:
                    umls_Score = umls_ent[1]
                    umlsList += str(umls_Code) + " SCORE: " + str(umls_Score) + "\n"
                    count += 1
                elif TUI in tuiFilter and UMLS_Def is not None and "OBSOLETE" not in UMLS_Def:
                    umls_Score = umls_ent[1]
                    umlsList += str(umls_Code) + " SCORE: " + str(umls_Score) + "\n"
                    count += 1
        return (umlsList, count)


def REST_JSON_to_Read(text: Dict) -> str:
    results = text.get("results")
    response = ""
    for x in results:
        response += x.get("ui") + ": " + x.get("name") + " "
    return response
