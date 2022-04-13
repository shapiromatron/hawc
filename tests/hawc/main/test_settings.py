import os
from unittest import mock

from hawc.constants import FeatureFlags

TEST_ENV_VARIABLE = "_HAWC_FEATURE_FLAGS_TEST_"


class TestFeatureFlags:
    @mock.patch.dict(os.environ, {TEST_ENV_VARIABLE: '{"THIS_IS_AN_EXAMPLE":false}'})
    def test_env_false(self):
        flags = FeatureFlags.from_env(TEST_ENV_VARIABLE)
        assert flags.THIS_IS_AN_EXAMPLE is False

    @mock.patch.dict(os.environ, {TEST_ENV_VARIABLE: '{"THIS_IS_AN_EXAMPLE":true}'})
    def test_env_true(self):
        flags = FeatureFlags.from_env(TEST_ENV_VARIABLE)
        assert flags.THIS_IS_AN_EXAMPLE is True

    def test_no_env(self):
        assert TEST_ENV_VARIABLE not in os.environ
        flags = FeatureFlags.from_env(TEST_ENV_VARIABLE)
        assert flags.THIS_IS_AN_EXAMPLE is True
