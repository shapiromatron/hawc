# Clients and APIs

The development team maintains a number of clients and APIs that are used for development and for some user interfaces for the application. The same rules for authentication and authorization are in place to access data from HAWC assessments programmatically using the API or clients.  Access for assessments can only be modified using the HAWC website; they cannot be changed via the client or API at this time.

## Python HAWC client

A [HAWC client](https://pypi.org/project/hawc-client/) has been developed and is the recommended approach to programmatically add or fetch content
from a HAWC instance. To install the client (requires Python ≥ 3.9):

```bash
python -m pip install -U hawc-client
```

Using a notebook or python shell:

```python
from getpass import getpass
from hawc_client import HawcClient

client = HawcClient("https://hawcproject.org")

# Authentication is deployment specific. If the hawc deployment stores and manages user
# accounts directly, then you can login via the HAWC API to authenticate:
client.authenticate(email="me@me.com", password=getpass())

# For other deployments which use external authentication, a user should login via the browser
# as a normal user, and then view the token on their user profile:
client.set_authentication_token(token=getpass())

# get all references for an assessment
client.lit.references(assessment_id=123)
```

An interactive client also exists which downloads figures or visualizations:

```python
from getpass import getpass
from hawc_client import HawcClient

client = HawcClient("https://hawcproject.org")
client.set_authentication_token(getpass(), login=True)  # must set login to True

with client.interactive(headless=False) as iclient:
    iclient.download_visual(123, 'visual.png')
    iclient.download_data_pivot(456, 'data-pivot.png')
```

There are many more commands available in the HAWC client that aren't documented here. It is recommended to use an interactive terminal session using a jupyter notebook to browse the available methods and their docstrings for more details.

### Tutorials

Client tutorials for common operations are below:

- Literature: [Adding/modifying/deleting references](https://github.com/shapiromatron/hawc/blob/master/scripts/client/lit-crud-references.ipynb)
- Literature: [Tagging references](https://github.com/shapiromatron/hawc/blob/master/scripts/client/lit-tagging-references.ipynb)
- Risk of bias/study evaluation: [Adding evaluations](https://github.com/shapiromatron/hawc/blob/master/scripts/client/rob-evaluations.ipynb)
- Bioassay: [Creating bioassay data](https://github.com/shapiromatron/hawc/blob/master/scripts/client/bioassay-crud.ipynb)

### Changelog

#### [2025-1](https://pypi.org/project/hawc-client/2025.1/) (TBD)

* Add `unpublished` parameter to bmd dataset download
* Remove data pivot API endpoints; all behaviors can be accomplished using the visual API

#### [2024-4](https://pypi.org/project/hawc-client/2024.4/) (January 2025)

* Added assessment team member API endpoint to retrieve assessments a user is a member of
* Added literature tag API {create, update, delete, move} to modify tags

#### [2024-3](https://pypi.org/project/hawc-client/2024.3/) (October 2024)

* Update data pivot and visual output formats to return JSON
* Add a new BMDS Export to return dose-response data

#### [2024-2](https://pypi.org/project/hawc-client/2024.2/) (July 2024)

* Minor documentation and docstring updates

#### [2024-1](https://pypi.org/project/hawc-client/2024.1/) (February 2024)

* Add new interactive client for downloading visual and data pivots images
* Updated study evaluation/risk of bias APIs
* Add APIs to modify EffectTags, commonly used in animal and epi models
* Add APIs to modify epiv2 models
* Add APIs to modify Visuals and Data Pivots
* Add APIs to modify Assessments, Assessment Values, and Assessment Details

#### [2023-2](https://pypi.org/project/hawc-client/2023.2/) (April 2023)

* Add new `login` parameter to `client.set_authentication_token`, and returns  boolean instead of a dict.
    - If `login` is False (default), a token based API session is created. This is consistent with previous behavior.
    - If `login` is True, a django cookie-based session is set instead of a token-based API session. This may be used if using the client to browse the website, however CSRF tokens will be required for API and form requests.
* Added ``client.lit.reference_user_tags`` - retrieves all user tag for all references for an assessment.

#### [2023-1](https://pypi.org/project/hawc-client/2023.1/) (January 2023)

* Added ``client.riskofbias.compare_metrics`` - align metrics when copying across assessments via fuzzy text matching
* Added ``client.summary.datapivot_list`` - retrieve all data pivots for an assessment
* Added ``client.summary.table_list`` - retrieve all tables for an assessment

#### [2022-7](https://pypi.org/project/hawc-client/2022.7/) (July 2022)

* Added ``client.study.studies`` to return dataframe of studies for an assessment
* Added new parameter, ``invert``, to the ``client.animal.endpoints``
    * When invert is False (default), returns a list of endpoints with parent data nested
    * When invert is True, returns a list of studies, with child data nested
* Added ``client.riskofbias.metrics`` to return a dataframe of metrics for an assessment
* Added ``client.riskofbias.reviews`` to return a list of reviews for an assessment

## API access

Authenticated users can access HAWC REST APIs; below is an example script for use:

```python
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
```
