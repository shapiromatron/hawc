import os

import pytest

from hawc.apps.bmd.diagnostics import bmds2_service_healthcheck

has_bmds_service_url = "BMDS_SUBMISSION_URL" in os.environ


@pytest.mark.skipif(not has_bmds_service_url, reason="skip; submission url unset")
def test_bmds2_service_healthcheck():
    assert bmds2_service_healthcheck() is True
