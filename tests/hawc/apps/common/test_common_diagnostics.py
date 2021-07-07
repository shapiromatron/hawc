from matplotlib.axes import Axes

from hawc.apps.common.diagnostics import worker_healthcheck


def test_worker_healthcheck(monkeypatch, mock_redis):
    _conn = mock_redis()
    monkeypatch.setattr("hawc.apps.common.diagnostics.get_redis_connection", lambda: _conn)

    # no data; should be an error
    assert worker_healthcheck.healthy() is False
    assert worker_healthcheck.series().size == 0

    # has recent data; should be healthy
    for i in range(_conn.MAX_SIZE + 2):
        worker_healthcheck.push()
    assert worker_healthcheck.healthy() is True
    assert worker_healthcheck.series().size == _conn.MAX_SIZE
    assert isinstance(worker_healthcheck.plot(), Axes)  # should not fail

    # set an old date; should fail
    worker_healthcheck.clear()
    _conn.lpush(worker_healthcheck.KEY, 915148800.000000)  # party like its ...
    assert worker_healthcheck.healthy() is False
    assert worker_healthcheck.series().size == 1
    assert isinstance(worker_healthcheck.plot(), Axes)  # should not fail
