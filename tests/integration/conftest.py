import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache():
    """Prevent cached responses from leaking between browser tests."""
    cache.clear()
    yield
    cache.clear()
