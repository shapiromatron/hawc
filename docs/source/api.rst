API
===

Authenticated users can access HAWC REST APIs; below is an example script for use:

.. code-block:: python

    import requests

    session = requests.Session()
    login = requests.post(
        "https://hawcproject.org/user/api/token-auth/",
        json={"username": "me@me.com", "password": "keep-it-hidden"}
    )

    if login.status_code == 200:
        session.headers.update(Authorization=f"Token {login.json()['token']}")
    else:
        raise EnvironmentError("Authentication failed")

    session.get('https://hawcproject.org/ani/api/endpoint/?assessment_id=123').json()


There's also a HAWC client available:

.. code-block:: python

    from hawc_client import HawcClient

    client = HawcClient(root_url="https://hawcproject.org")
    client.authenticate(username="username",password="password")

    # as an example, get all references for an assessment
    client.lit.references(assessment_id=123)

    # as an example, import new references to an assessment
    client.lit.import_hero(
        assessment_id=123,
        title="example title",
        description="example description",
        ids=[5000,5010]
    )

There's also a HAWC client available in R:

.. code-block:: R

    devtools::install_github('shapiromatron/hawc', subdir='client/r/rhawc')
    library(rhawc)

    client = HawcClient("https://hawcproject.org")
    client$authenticate("me@me.com", "keep-it-hidden")

    hero_ids = list(500:520)
    client$lit_import_hero(
        assessment_id=123,
        title="example title",
        description="example description",
        ids=hero_ids
    )

