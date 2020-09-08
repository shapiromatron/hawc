import re
from typing import Any, List

# First-group is rest of reference; second-group are initials
# with optional second initial (middle-name) with optional periods
RE_AUTHOR = re.compile(r"([\-\,\w]+)\s([\s?\w{1,1}\.?]+)$", flags=re.UNICODE)
RE_TWO_INITIALS = re.compile(r"^([\w])[\,\.]{0,2}\s([\w])[\,\.]{0,2}$", flags=re.UNICODE)


def normalize_author(author: str) -> str:
    # for cases which may appear to be to be an individual's name
    num_words = len(author.split())
    if num_words > 1 and num_words < 4:
        matches = RE_AUTHOR.match(author)
        if matches:
            matches2 = RE_TWO_INITIALS.match(matches.group(2))
            if matches2:
                initials = matches.group(2).replace(",", "").replace(".", "").replace(" ", "")
            else:
                initials = matches.group(2).replace(",", "").replace(".", "")

            surname = matches.group(1).replace(",", "")
            author = f"{surname} {initials}"
    return author


def normalize_authors(authors: List[str]) -> List[str]:
    return [normalize_author(author) for author in authors]


def get_author_short_text(authors: List[str]) -> str:
    # Given a list of authors, return citation.
    n_authors = len(authors)
    if n_authors == 0:
        return ""
    elif n_authors == 1:
        return str(authors[0])
    elif n_authors == 2:
        return "{0} and {1}".format(*authors)
    elif n_authors == 3:
        return "{0}, {1}, and {2}".format(*authors)
    else:  # >3 authors
        return f"{authors[0]} et al."


def try_int(val) -> Any:
    try:
        return int(val)
    except Exception:
        return val
