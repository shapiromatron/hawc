import pytest
from pydantic import ValidationError

from hawc.apps.common.dynamic_forms.fields import _Field


class TestField:
    def test_name_regex(self):
        for name in ["valid", "VALID", "aZ_1"]:
            _Field(name=name)

        for name in ["a space", "a+plus", "a.dot"]:
            with pytest.raises(ValidationError):
                _Field(name=name)
