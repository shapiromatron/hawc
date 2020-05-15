Clients and APIs
================

The development team maintains a number of clients and APIs that are used for development and for some user interfaces for the application. The same rules for authentication and authorization are in place to access data from HAWC assessments programmatically using the API or clients.  Access for assessments can only be modified using the HAWC website; they cannot be changed via the client or API at this time.

Python HAWC client
------------------

A `HAWC client`_ has been developed and is the recommended approach to programmatically add or fetch content
from a HAWC instance. To install the client (requires Python ≥ 3.6):

.. _`HAWC client`: https://pypi.org/project/hawc-client/

.. code-block:: bash

    pip install hawc-client

Using a notebook or python shell:

.. code-block:: python

    from hawc_client import HawcClient

    client = HawcClient(root_url="https://hawcproject.org")
    client.authenticate(username="username",password="password")

    # get all references for an assessment
    client.lit.references(assessment_id=123)

    # import new references to an assessment
    client.lit.import_hero(
        assessment_id=123,
        title="example title",
        description="example description",
        ids=[5000,5010]
    )

There are many more commands available in the HAWC client that aren't documented here. It is recommended to use an interactive terminal session using a notebook or ipython to browse the available methods and their docstrings for more details.

R HAWC client
-------------

An R client is also available. To install and use:

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

Please note that the Python client is considered the reference implementation for a HAWC client and will include the latest features; the R client may be a little behind.

API access
----------

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
