Clients and APIs
================

The development team maintains a number of clients and APIs that are used for development and for some user interfaces for the application. The same rules for authentication and authorization are in place to access data from HAWC assessments programmatically using the API or clients.  Access for assessments can only be modified using the HAWC website; they cannot be changed via the client or API at this time.

Python HAWC client
------------------

A `HAWC client`_ has been developed and is the recommended approach to programmatically add or fetch content
from a HAWC instance. To install the client (requires Python ≥ 3.9):

.. _`HAWC client`: https://pypi.org/project/hawc-client/

.. code-block:: bash

    pip install hawc-client

Using a notebook or python shell:

.. code-block:: python

    from getpass import getpass
    from hawc_client import HawcClient

    client = HawcClient("https://hawcproject.org")

    # Authentication is deployment specific. If the hawc deployment stores and managers user
    # accounts directly, then you can login via the HAWC API to authenticate:
    client.authenticate(email="me@me.com", password=getpass())

    # For other deployments which use external authentication, a user should login via the browser
    # as a normal user, and then view the token on their user profile:
    client.set_authentication_token(token=getpass())

    # get all references for an assessment
    client.lit.references(assessment_id=123)

There are many more commands available in the HAWC client that aren't documented here. It is recommended to use an interactive terminal session using a jupyter notebook to browse the available methods and their docstrings for more details.

Tutorials
~~~~~~~~~

Client tutorials for common operations are below:

- Literature: `Adding/modifying/deleting references`_
- Literature: `Tagging references`_
- Risk of bias/study evaluation: `Adding evaluations`_
- Bioassay: `Creating bioassay data`_

.. _`Adding/modifying/deleting references`: https://github.com/shapiromatron/hawc/blob/master/scripts/client/lit-crud-references.ipynb
.. _`Tagging references`:                   https://github.com/shapiromatron/hawc/blob/master/scripts/client/lit-tagging-references.ipynb
.. _`Adding evaluations`:                   https://github.com/shapiromatron/hawc/blob/master/scripts/client/rob-evaluations.ipynb
.. _`Creating bioassay data`:               https://github.com/shapiromatron/hawc/blob/master/scripts/client/bioassay-crud.ipynb

R HAWC client
-------------

An R client is also available. To install and use:

.. code-block:: R

    devtools::install_github('shapiromatron/hawc', subdir='client/r/rhawc')
    library(rhawc)

    client = HawcClient("https://hawcproject.org")
    client$authenticate("me@me.com", getPass::getPass())

    # get all references for an assessment
    client$lit_references(assessment_id=123)

Please note that the Python client is considered the reference implementation for a HAWC client and will include the latest features; the R client may be a little behind. A high-level notebook we use for testing is available to see how the R client works: `R tutorial`_. For more detailed trainings, see the Python notebook tutorials above.

.. _`R tutorial`: https://github.com/shapiromatron/hawc/blob/master/scripts/client/r-client.ipynb

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
