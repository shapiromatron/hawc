import html
import json
import urllib.parse

from hawc.apps.lit import constants


def get_doi_if_valid(text: str):
    doi = constants.DOI_EXTRACT.search(text)
    if doi:
        doi = doi.group(0)
        doi = html.unescape(doi)
        doi = urllib.parse.unquote(doi)
        while doi.endswith((".", ",", '"')):
            doi = doi[:-1]
        ind = doi.find("</ArticleId>")
        if ind != -1:
            doi = doi[:ind]
        ind = doi.find("</ELocationID>")
        if ind != -1:
            doi = doi[:ind]
    return doi


def get_doi_from_hero(ident):
    try:
        doi = json.loads(ident.content)["json"]["doi"]
    except (KeyError):
        try:
            doi = json.loads(ident.content)["doi"]
        except (KeyError):
            doi = None
    doi = get_doi_if_valid(str(doi))
    return doi


def get_doi_from_pubmed(ident):
    try:
        doi = json.loads(ident.content)["doi"]
    except (KeyError):
        doi = None
    doi = get_doi_if_valid(str(doi))
    return doi


def get_doi_from_ris(ident):
    try:
        doi = json.loads(ident.content)["doi"]
    except (KeyError):
        doi = None
    doi = get_doi_if_valid(str(doi))
    return doi
