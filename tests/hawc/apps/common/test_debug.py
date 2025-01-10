import logging
import time

from hawc.apps.common.debug import time_logger


def test_time_logger(caplog):
    @time_logger
    def sample_function():
        time.sleep(0.0001)
        return "done"

    with caplog.at_level(logging.INFO):
        result = sample_function()
        assert result == "done"
        assert len(caplog.records) == 1
        assert "Function 'sample_function' took" in caplog.records[0].message
