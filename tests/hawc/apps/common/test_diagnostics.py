import pytest
from django.conf import settings
from matplotlib.axes import Axes

from hawc.apps.common.diagnostics import worker_healthcheck


def has_redis():
    return "RedisCache" in settings.CACHES["default"]["BACKEND"]


@pytest.mark.skipif(not has_redis(), reason="skip; redis cache required")
def test_worker_healthcheck():
    conn = worker_healthcheck._get_conn()
    worker_healthcheck.clear()

    # no data; should be an error
    assert worker_healthcheck.healthy() is False
    assert worker_healthcheck.series().size == 0

    # has recent data; should be healthy
    worker_healthcheck.MAX_SIZE = 5
    for _i in range(worker_healthcheck.MAX_SIZE + 2):
        worker_healthcheck.push()
    assert worker_healthcheck.healthy() is True
    assert worker_healthcheck.series().size == worker_healthcheck.MAX_SIZE
    assert isinstance(worker_healthcheck.plot(), Axes)  # should not fail

    # set an old date; should fail
    worker_healthcheck.clear()
    conn = worker_healthcheck._get_conn()
    conn.lpush(worker_healthcheck.KEY, 915148800.000000)  # party like its ...
    assert worker_healthcheck.healthy() is False
    assert worker_healthcheck.series().size == 1
    assert isinstance(worker_healthcheck.plot(), Axes)  # should not fail
