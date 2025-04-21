import pandas as pd

from ..models import Endpoint


def term_check(assessment_id: int) -> pd.DataFrame:
    """
    Generate a report for potential issues identified in a given assessment and
    the current EHV vocabulary.
    """
    fields = ["system", "organ", "effect", "effect_subtype", "name"]
    related = [f"{field}_term" for field in fields]
    data = []
    for endpoint in Endpoint.objects.filter(assessment_id=assessment_id).select_related(*related):
        row1 = [endpoint.assessment_id, endpoint.id, endpoint.get_absolute_url()]
        for idx, field in enumerate(fields):
            text = getattr(endpoint, field)
            term = getattr(endpoint, f"{field}_term")

            # only continue checks if a term exists
            if term is None:
                continue

            # Check if term is deprecated
            if term.deprecated_on is not None:
                row2 = list(row1)
                row2.extend(
                    [
                        field,
                        text,
                        term.name,
                        term.id,
                        "Term is deprecated",
                        f'Term "{term.name}" ({term.id}) is deprecated',
                    ]
                )
                data.append(row2)

            # check if endpoint free text matches term text
            if text != term.name:
                row2 = list(row1)
                row2.extend(
                    [
                        field,
                        text,
                        term.name,
                        term.id,
                        "Endpoint free text does not match Term text",
                        f'{field} text "{text}" != Term "{term.name}" ({term.id})',
                    ]
                )
                data.append(row2)

            if idx > 0:
                parent_term = getattr(endpoint, f"{fields[idx - 1]}_term")

                # check if a child term exists, but a parent does not
                if parent_term is None:
                    row2 = list(row1)
                    row2.extend(
                        [
                            field,
                            text,
                            term.name,
                            term.id,
                            "Parent term not specified",
                            f'"{field}" term exists but "{fields[idx - 1]}" term not set - use {term.parent.name} ({term.parent.id})?',
                        ]
                    )
                    data.append(row2)

                # check if the parent term in the vocabulary matches the term on the endpoint
                if parent_term and parent_term.id != term.parent_id:
                    row2 = list(row1)
                    row2.extend(
                        [
                            field,
                            text,
                            term.name,
                            term.id,
                            "Parent term on endpoint does not match parent term in vocabulary",
                            f"The {field} parent vocabulary term is {term.parent.name} ({term.parent.id}); this endpoint specified {parent_term.name} ({parent_term.id})",
                        ]
                    )
                    data.append(row2)

    df = (
        pd.DataFrame(
            columns=[
                "assessment_id",
                "endpoint_id",
                "endpoint_url",
                "term_type",
                "endpoint_term_free_text",
                "vocabulary_term_text",
                "vocabulary_term_id",
                "issue_class",
                "issue_description",
            ],
            data=data,
        )
        .sort_values(["assessment_id", "endpoint_id"])
        .reset_index(drop=True)
    )
    return df
