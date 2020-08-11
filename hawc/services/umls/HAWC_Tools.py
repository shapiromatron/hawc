from __future__ import print_function
from Authentication import *
import requests
import numpy as np
import json
import pandas as pd
import spacy
import scispacy
from scispacy.umls_linking import UmlsEntityLinker
import os, sys





def UMLS_RestLookup(string, apikey ): #, umls_dictionary = umls_dictionary):
    umls_dictionary = dict()
    while True:
        if string in umls_dictionary:
            jsonData = umls_dictionary.get(string)
            print("Pulled from dictionary:  " + string)
        else:
            uri = "https://uts-ws.nlm.nih.gov"
            content_endpoint = "/rest/search/current"
            pageNumber=0
            AuthClient = Authentication(apikey)
            tgt = AuthClient.gettgt()
            ticket = AuthClient.getst(tgt)
            pageNumber += 1
            query = {'string':string,'ticket':ticket, 'pageNumber':pageNumber}
            query["inputType"] = "atom"
            query['includeObsolete'] = 'false'
            query['includeSuppressible'] = 'false'
            query['searchType'] = "exact"
            query['pageNumber'] = 1
            query['pageSize'] = 3
            # query['sabs'] = "MTH"
            r = requests.get(uri+content_endpoint,params=query)
            r.encoding = 'utf-8'
            items  = json.loads(r.text)
            jsonData = items["result"]
            print("Pulled from API:  " + string)
            umls_dictionary[string] = jsonData
        return(jsonData)


def loadUMLSLinker(max_UMLS_Returns, confidence, model = "en_core_sci_sm"):
    nlp = spacy.load(model)
    linker = UmlsEntityLinker(resolve_abbreviations=False, max_entities_per_mention=max_UMLS_Returns, threshold=confidence)
    nlp.add_pipe(linker)
    return(linker, nlp)

def flipOnComma(text):
    text_split = text.split(",")
    text_flipped = text_split[::-1]
    text_joined = " ".join(map(str,text_flipped)).strip()
    return(text_joined)

def breakIntoEntities(text, nlp):
    doc = nlp(text)
    entities = doc.ents
    return(entities)


def breakIntoSpansAndUMLS(text, nlp, linker, tuiFilter = [], RequireNonObsoleteDef=False):
    doc = nlp(text.strip())
    entity = doc[:]
    umlsList = ""
    count = 0
    for umls_ent in entity._.umls_ents:
        umls_Code = linker.umls.cui_to_entity[umls_ent[0]] 
        TUI = umls_Code[3]
        UMLS_Def = umls_Code[4]
        if RequireNonObsoleteDef == False:
            if tuiFilter == [] :
                umls_Score = umls_ent[1]
                umlsList += (str(umls_Code) + " SCORE: " + str(umls_Score)  + "\n" )
                count += 1 
            elif any(x in TUI for x in tuiFilter) :
                umls_Score = umls_ent[1]
                umlsList += (str(umls_Code) + " SCORE: " + str(umls_Score)  + "\n" )
                count += 1 
        elif RequireNonObsoleteDef == True:
            if UMLS_Def== None or"OBSOLETE" in UMLS_Def :
                pass           
            elif tuiFilter == [] and UMLS_Def != None and "OBSOLETE" not in UMLS_Def:
                umls_Score = umls_ent[1]
                umlsList += (str(umls_Code) + " SCORE: " + str(umls_Score)  + "\n" )
                count += 1 
            elif any(x in TUI for x in tuiFilter) and UMLS_Def != None and "OBSOLETE" not in UMLS_Def:
                umls_Score = umls_ent[1]
                umlsList += (str(umls_Code) + " SCORE: " + str(umls_Score)  + "\n" )
                count += 1    
    return(umlsList, count)

def breakIntoEntitiesAndUMLS(text, nlp, linker, tuiFilter = [], RequireNonObsoleteDef = False):
    umlsList = ""
    doc = nlp(text)
    entities = doc.ents
    count = 0
    for entity in entities:
        for umls_ent in entity._.umls_ents:
            umls_Code = linker.umls.cui_to_entity[umls_ent[0]] 
            TUI = umls_Code[3]
            UMLS_Def = umls_Code[4]
            if RequireNonObsoleteDef == False:
                if tuiFilter == [] :
                    umls_Score = umls_ent[1]
                    umlsList += (str(umls_Code) + " SCORE: " + str(umls_Score)  + "\n" )
                    count += 1 
                elif any(x in TUI for x in tuiFilter) :
                    umls_Score = umls_ent[1]
                    umlsList += (str(umls_Code) + " SCORE: " + str(umls_Score)  + "\n" )
                    count += 1 
            elif RequireNonObsoleteDef == True:
                if UMLS_Def== None or"OBSOLETE" in UMLS_Def :
                    pass           
                elif tuiFilter == [] and UMLS_Def != None and "OBSOLETE" not in UMLS_Def:
                    umls_Score = umls_ent[1]
                    umlsList += (str(umls_Code) + " SCORE: " + str(umls_Score)  + "\n" )
                    count += 1 
                elif any(x in TUI for x in tuiFilter) and UMLS_Def != None and "OBSOLETE" not in UMLS_Def:
                    umls_Score = umls_ent[1]
                    umlsList += (str(umls_Code) + " SCORE: " + str(umls_Score)  + "\n" )
                    count += 1    
        return(umlsList, count)


def REST_JSON_to_Read(text):
    results = (text.get("results"))
    FinalResults = ''
    for x in results:
        FinalResults += (x.get('ui') + ": " + x.get("name") + " ")
    return(FinalResults)

       


