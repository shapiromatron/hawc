import html
import json
import urllib.parse

from hawc.apps.lit.constants import DOI_EXTRACT


def try_get_doi(text: str, full_text: bool = False) -> str | None:
    """Try to extract a DOI out of text.

    Args:
        text (str): The text to find a DOI
        full_text (bool, optional): Additional checks if unstructured text, default False.

    Returns:
        Optional[str]: A DOI string if one can be found
    """
    # empty string or None
    if not isinstance(text, str):
        return None
    text = html.unescape(text)
    text = urllib.parse.unquote(text)
    if doi := DOI_EXTRACT.search(text):
        doi = doi.group(0)
        if full_text:
            # there may be multiple trailing invalid characters
            while doi.endswith((".", ",", '"')):
                doi = doi[:-1]
            if (index := doi.find("</ArticleId>")) >= 0:
                doi = doi[:index]
            if (index2 := doi.find("</ELocationID>")) >= 0:
                doi = doi[:index2]
    return doi.lower() if doi else None


def get_doi_from_identifier(ident) -> str | None:
    try:
        data = json.loads(ident.content)
    except json.JSONDecodeError:
        return None
    if "doi" in data:
        return try_get_doi(data["doi"])
    if "json" in data and "doi" in data["json"]:
        return try_get_doi(data["json"]["doi"])
    return None
