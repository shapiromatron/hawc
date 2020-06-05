import os

import pytest

in_ci = os.environ.get("GITHUB_RUN_ID") is not None


@pytest.mark.skipif(not in_ci, reason="only run in CI")
def test_rewrite_flag(rewrite_data_files):
    """
    safety check- rewrite datafiles must be False in CI; otherwise we'd just rewrite
    data every-time and our tests would always pass
    """
    if rewrite_data_files is True:
        raise ValueError("Fixture `rewrite_data_files` must be `False`.")
